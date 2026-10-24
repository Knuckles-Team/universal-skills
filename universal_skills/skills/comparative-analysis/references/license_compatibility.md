# License Compatibility Matrix

## OSI-Approved License Categories

### Permissive Licenses (Most Compatible)
| License | SPDX ID | Commercial Use | Modification | Distribution | Patent Grant |
|---------|---------|---------------|--------------|--------------|-------------|
| MIT | MIT | ✅ | ✅ | ✅ | ❌ |
| Apache 2.0 | Apache-2.0 | ✅ | ✅ | ✅ | ✅ |
| BSD 2-Clause | BSD-2-Clause | ✅ | ✅ | ✅ | ❌ |
| BSD 3-Clause | BSD-3-Clause | ✅ | ✅ | ✅ | ❌ |
| ISC | ISC | ✅ | ✅ | ✅ | ❌ |
| Unlicense | Unlicense | ✅ | ✅ | ✅ | ❌ |

### Copyleft Licenses (Restrictive)
| License | SPDX ID | Commercial Use | Modification | Distribution | Copyleft |
|---------|---------|---------------|--------------|--------------|---------|
| GPL 2.0 | GPL-2.0-only | ✅ | ✅ | ✅ (same license) | Strong |
| GPL 3.0 | GPL-3.0-only | ✅ | ✅ | ✅ (same license) | Strong |
| LGPL 2.1 | LGPL-2.1-only | ✅ | ✅ | ✅ (weak copyleft) | Weak |
| LGPL 3.0 | LGPL-3.0-only | ✅ | ✅ | ✅ (weak copyleft) | Weak |
| AGPL 3.0 | AGPL-3.0-only | ✅ | ✅ | ✅ (network use) | Network |
| MPL 2.0 | MPL-2.0 | ✅ | ✅ | ✅ (file-level) | File |

### Compatibility Matrix

Can code under License A be combined with code under License B?

| ↓ A \ B → | MIT | Apache-2.0 | GPL-2.0 | GPL-3.0 | LGPL-2.1 | AGPL-3.0 | MPL-2.0 |
|-----------|-----|-----------|---------|---------|----------|----------|---------|
| **MIT** | ✅ | ✅ | ✅→GPL | ✅→GPL | ✅ | ✅→AGPL | ✅ |
| **Apache-2.0** | ✅ | ✅ | ❌ | ✅→GPL3 | ✅ | ✅→AGPL | ✅ |
| **GPL-2.0** | ✅←GPL | ❌ | ✅ | ❌ | ✅←GPL | ❌ | ❌ |
| **GPL-3.0** | ✅←GPL | ✅←GPL3 | ❌ | ✅ | ✅←GPL3 | ✅←AGPL | ✅←GPL3 |
| **LGPL-2.1** | ✅ | ✅ | ✅←GPL | ✅←GPL3 | ✅ | ✅←AGPL | ✅ |
| **AGPL-3.0** | ✅←AGPL | ✅←AGPL | ❌ | ✅←AGPL | ✅←AGPL | ✅ | ✅←AGPL |
| **MPL-2.0** | ✅ | ✅ | ❌ | ✅←GPL3 | ✅ | ✅←AGPL | ✅ |

### Key
- ✅ = Compatible
- ❌ = Incompatible
- ✅→X = Combined work must be under license X
- ✅←X = The A-licensed portion triggers X

## Enterprise Considerations

### License Risk Tiers
| Tier | Risk Level | Licenses | Enterprise Impact |
|------|-----------|----------|-------------------|
| **Green** | Low | MIT, Apache-2.0, BSD | Free to use commercially |
| **Yellow** | Medium | LGPL, MPL | Linking restrictions, file-level copyleft |
| **Red** | High | GPL, AGPL | Strong copyleft, disclosure obligations |
| **Black** | Prohibited | SSPL, Commons Clause, BSL | Non-OSI, commercial restrictions |

### Scoring Criteria
- Green license: +10 points
- Yellow license: +5 points
- Red license: 0 points
- Black/No license: -10 points
- License file present: +5 points
- SPDX identifier in metadata: +5 points
