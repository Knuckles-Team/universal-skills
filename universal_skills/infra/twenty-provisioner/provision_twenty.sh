#!/usr/bin/env bash
# Day-0 Twenty provisioning — mint a long-lived API key from credentials, headlessly.
#
# Twenty serves its CORE/auth/system GraphQL schema at **/metadata** (NOT /graphql,
# which is only the per-workspace object schema). This script reproduces the verified
# flow: (signUp once) -> getLoginTokenFromCredentials -> getAuthTokensFromLoginToken
# -> getRoles -> createApiKey -> generateApiKeyToken, then validates against /rest.
#
# Usage:
#   TWENTY_URL=http://twenty.arpa \
#   TWENTY_EMAIL=admin@homelab.arpa TWENTY_PASSWORD='...' \
#   [SIGNUP=1] [KEY_NAME=egeria-harvester] [EXPIRES_AT=2125-01-01T00:00:00.000Z] \
#   bash provision_twenty.sh
#
# On success, prints the API key to stdout (capture it; it is shown once) and exits 0.
# Requires: curl, jq.
set -uo pipefail

URL="${TWENTY_URL:?set TWENTY_URL (e.g. http://twenty.arpa)}"
EMAIL="${TWENTY_EMAIL:?set TWENTY_EMAIL}"
PASSWORD="${TWENTY_PASSWORD:?set TWENTY_PASSWORD}"
KEY_NAME="${KEY_NAME:-egeria-harvester}"
EXPIRES_AT="${EXPIRES_AT:-2125-01-01T00:00:00.000Z}"
META="$URL/metadata"
H=(-H 'Content-Type: application/json' -H "Origin: $URL")

gql() { # $1=query  $2=variables-json  [$3=bearer]
  local auth=(); [ -n "${3:-}" ] && auth=(-H "Authorization: Bearer $3")
  curl -s -m 20 -X POST "$META" "${H[@]}" "${auth[@]}" \
    --data "$(jq -nc --arg q "$1" --argjson v "$2" '{query:$q,variables:$v}')"
}
die() { echo "ERROR: $*" >&2; exit 1; }

# 0. Optional first-user signup (idempotent-ish: ignore "already exists")
if [ "${SIGNUP:-0}" = "1" ]; then
  >&2 echo "[provision] signUp $EMAIL ..."
  gql 'mutation($email:String!,$password:String!,$origin:String!){ signUp(email:$email,password:$password,origin:$origin){ loginToken{ token } } }' \
      "$(jq -nc --arg e "$EMAIL" --arg p "$PASSWORD" --arg o "$URL" '{email:$e,password:$p,origin:$o}')" \
      | jq -rc '.errors[0].message // "signUp ok"' >&2
fi

# 1. login -> loginToken
>&2 echo "[provision] getLoginTokenFromCredentials ..."
LT=$(gql 'mutation($email:String!,$password:String!,$origin:String!){ getLoginTokenFromCredentials(email:$email,password:$password,origin:$origin){ loginToken{ token } } }' \
    "$(jq -nc --arg e "$EMAIL" --arg p "$PASSWORD" --arg o "$URL" '{email:$e,password:$p,origin:$o}')" \
    | jq -r '.data.getLoginTokenFromCredentials.loginToken.token // empty')
[ -n "$LT" ] || die "login failed (check email/password/origin)"

# 2. loginToken -> access token
>&2 echo "[provision] getAuthTokensFromLoginToken ..."
AT=$(gql 'mutation($loginToken:String!,$origin:String!){ getAuthTokensFromLoginToken(loginToken:$loginToken,origin:$origin){ tokens{ accessOrWorkspaceAgnosticToken{ token } } } }' \
    "$(jq -nc --arg lt "$LT" --arg o "$URL" '{loginToken:$lt,origin:$o}')" \
    | jq -r '.data.getAuthTokensFromLoginToken.tokens.accessOrWorkspaceAgnosticToken.token // empty')
[ -n "$AT" ] || die "token exchange failed"

# 3. pick a role (Admin = canUpdateAllSettings)
>&2 echo "[provision] getRoles ..."
RID=$(gql 'query{ getRoles{ id label canUpdateAllSettings } }' '{}' "$AT" \
    | jq -r '(.data.getRoles[]? | select(.canUpdateAllSettings==true) | .id) // (.data.getRoles[0].id) // empty' | head -1)
[ -n "$RID" ] || die "no roles returned"

# 4. createApiKey (role-scoped)
>&2 echo "[provision] createApiKey ..."
KID=$(gql 'mutation($name:String!,$expiresAt:String!,$roleId:UUID!){ createApiKey(input:{name:$name,expiresAt:$expiresAt,roleId:$roleId}){ id } }' \
    "$(jq -nc --arg n "$KEY_NAME" --arg e "$EXPIRES_AT" --arg r "$RID" '{name:$n,expiresAt:$e,roleId:$r}')" "$AT" \
    | jq -r '.data.createApiKey.id // empty')
[ -n "$KID" ] || die "createApiKey failed"

# 5. generateApiKeyToken  (apiKeyId:UUID!, expiresAt:String!)
>&2 echo "[provision] generateApiKeyToken ..."
AK=$(gql 'mutation($apiKeyId:UUID!,$expiresAt:String!){ generateApiKeyToken(apiKeyId:$apiKeyId,expiresAt:$expiresAt){ token } }' \
    "$(jq -nc --arg id "$KID" --arg e "$EXPIRES_AT" '{apiKeyId:$id,expiresAt:$e}')" "$AT" \
    | jq -r '.data.generateApiKeyToken.token // empty')
[ -n "$AK" ] || die "generateApiKeyToken failed"

# 6. validate against /rest
code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $AK" -H 'Accept: application/json' "$URL/rest/companies?limit=1")
>&2 echo "[provision] validate /rest/companies -> http=$code (expect 200)"
[ "$code" = "200" ] || die "minted key failed /rest validation (http=$code)"

>&2 echo "[provision] SUCCESS (api_key_id=$KID)"
printf '%s\n' "$AK"   # the API key — capture this (shown once)
