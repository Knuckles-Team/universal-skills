# Jellyfin MCP Reference

**Project:** `jellyfin-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `JELLYFIN_URL` | Required for authentication |
| `JELLYFIN_API_KEY` | Required for authentication |

## Available Tool Tags (62)

| Env Variable | Default |
|-------------|----------|
| `ACTIVITYLOGTOOL` | `True` |
| `APIKEYTOOL` | `True` |
| `ARTISTSTOOL` | `True` |
| `AUDIOTOOL` | `True` |
| `BACKUPTOOL` | `True` |
| `BRANDINGTOOL` | `True` |
| `CHANNELSTOOL` | `True` |
| `CLIENTLOGTOOL` | `True` |
| `COLLECTIONTOOL` | `True` |
| `CONFIGURATIONTOOL` | `True` |
| `DASHBOARDTOOL` | `True` |
| `DEVICESTOOL` | `True` |
| `DISPLAYPREFERENCESTOOL` | `True` |
| `DYNAMICHLSTOOL` | `True` |
| `ENVIRONMENTTOOL` | `True` |
| `FILTERTOOL` | `True` |
| `GENRESTOOL` | `True` |
| `HLSSEGMENTTOOL` | `True` |
| `IMAGETOOL` | `True` |
| `INSTANTMIXTOOL` | `True` |
| `ITEMLOOKUPTOOL` | `True` |
| `ITEMREFRESHTOOL` | `True` |
| `ITEMSTOOL` | `True` |
| `ITEMUPDATETOOL` | `True` |
| `LIBRARYSTRUCTURETOOL` | `True` |
| `LIBRARYTOOL` | `True` |
| `LIVETVTOOL` | `True` |
| `LOCALIZATIONTOOL` | `True` |
| `LYRICSTOOL` | `True` |
| `MEDIAINFOTOOL` | `True` |
| `MEDIASEGMENTSTOOL` | `True` |
| `MISCTOOL` | `True` |
| `MOVIESTOOL` | `True` |
| `MUSICGENRESTOOL` | `True` |
| `PACKAGETOOL` | `True` |
| `PERSONSTOOL` | `True` |
| `PLAYLISTSTOOL` | `True` |
| `PLAYSTATETOOL` | `True` |
| `PLUGINSTOOL` | `True` |
| `QUICKCONNECTTOOL` | `True` |
| `REMOTEIMAGETOOL` | `True` |
| `SCHEDULEDTASKSTOOL` | `True` |
| `SEARCHTOOL` | `True` |
| `SESSIONTOOL` | `True` |
| `STARTUPTOOL` | `True` |
| `STUDIOSTOOL` | `True` |
| `SUBTITLETOOL` | `True` |
| `SUGGESTIONSTOOL` | `True` |
| `SYNCPLAYTOOL` | `True` |
| `SYSTEMTOOL` | `True` |
| `TIMESYNCTOOL` | `True` |
| `TMDBTOOL` | `True` |
| `TRAILERSTOOL` | `True` |
| `TRICKPLAYTOOL` | `True` |
| `TVSHOWSTOOL` | `True` |
| `UNIVERSALAUDIOTOOL` | `True` |
| `USERLIBRARYTOOL` | `True` |
| `USERTOOL` | `True` |
| `USERVIEWSTOOL` | `True` |
| `VIDEOATTACHMENTSTOOL` | `True` |
| `VIDEOSTOOL` | `True` |
| `YEARSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "jellyfin-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "JELLYFIN_URL": "${JELLYFIN_URL}",
        "JELLYFIN_API_KEY": "${JELLYFIN_API_KEY}",
        "ACTIVITYLOGTOOL": "True",
        "APIKEYTOOL": "True",
        "ARTISTSTOOL": "True",
        "AUDIOTOOL": "True",
        "BACKUPTOOL": "True",
        "BRANDINGTOOL": "True",
        "CHANNELSTOOL": "True",
        "CLIENTLOGTOOL": "True",
        "COLLECTIONTOOL": "True",
        "CONFIGURATIONTOOL": "True",
        "DASHBOARDTOOL": "True",
        "DEVICESTOOL": "True",
        "DISPLAYPREFERENCESTOOL": "True",
        "DYNAMICHLSTOOL": "True",
        "ENVIRONMENTTOOL": "True",
        "FILTERTOOL": "True",
        "GENRESTOOL": "True",
        "HLSSEGMENTTOOL": "True",
        "IMAGETOOL": "True",
        "INSTANTMIXTOOL": "True",
        "ITEMLOOKUPTOOL": "True",
        "ITEMREFRESHTOOL": "True",
        "ITEMSTOOL": "True",
        "ITEMUPDATETOOL": "True",
        "LIBRARYSTRUCTURETOOL": "True",
        "LIBRARYTOOL": "True",
        "LIVETVTOOL": "True",
        "LOCALIZATIONTOOL": "True",
        "LYRICSTOOL": "True",
        "MEDIAINFOTOOL": "True",
        "MEDIASEGMENTSTOOL": "True",
        "MISCTOOL": "True",
        "MOVIESTOOL": "True",
        "MUSICGENRESTOOL": "True",
        "PACKAGETOOL": "True",
        "PERSONSTOOL": "True",
        "PLAYLISTSTOOL": "True",
        "PLAYSTATETOOL": "True",
        "PLUGINSTOOL": "True",
        "QUICKCONNECTTOOL": "True",
        "REMOTEIMAGETOOL": "True",
        "SCHEDULEDTASKSTOOL": "True",
        "SEARCHTOOL": "True",
        "SESSIONTOOL": "True",
        "STARTUPTOOL": "True",
        "STUDIOSTOOL": "True",
        "SUBTITLETOOL": "True",
        "SUGGESTIONSTOOL": "True",
        "SYNCPLAYTOOL": "True",
        "SYSTEMTOOL": "True",
        "TIMESYNCTOOL": "True",
        "TMDBTOOL": "True",
        "TRAILERSTOOL": "True",
        "TRICKPLAYTOOL": "True",
        "TVSHOWSTOOL": "True",
        "UNIVERSALAUDIOTOOL": "True",
        "USERLIBRARYTOOL": "True",
        "USERTOOL": "True",
        "USERVIEWSTOOL": "True",
        "VIDEOATTACHMENTSTOOL": "True",
        "VIDEOSTOOL": "True",
        "YEARSTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "url": "http://jellyfin-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `ACTIVITYLOGTOOL` and disable all others:

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "jellyfin-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "JELLYFIN_URL": "${JELLYFIN_URL}",
        "JELLYFIN_API_KEY": "${JELLYFIN_API_KEY}",
        "ACTIVITYLOGTOOL": "True",
        "APIKEYTOOL": "False",
        "ARTISTSTOOL": "False",
        "AUDIOTOOL": "False",
        "BACKUPTOOL": "False",
        "BRANDINGTOOL": "False",
        "CHANNELSTOOL": "False",
        "CLIENTLOGTOOL": "False",
        "COLLECTIONTOOL": "False",
        "CONFIGURATIONTOOL": "False",
        "DASHBOARDTOOL": "False",
        "DEVICESTOOL": "False",
        "DISPLAYPREFERENCESTOOL": "False",
        "DYNAMICHLSTOOL": "False",
        "ENVIRONMENTTOOL": "False",
        "FILTERTOOL": "False",
        "GENRESTOOL": "False",
        "HLSSEGMENTTOOL": "False",
        "IMAGETOOL": "False",
        "INSTANTMIXTOOL": "False",
        "ITEMLOOKUPTOOL": "False",
        "ITEMREFRESHTOOL": "False",
        "ITEMSTOOL": "False",
        "ITEMUPDATETOOL": "False",
        "LIBRARYSTRUCTURETOOL": "False",
        "LIBRARYTOOL": "False",
        "LIVETVTOOL": "False",
        "LOCALIZATIONTOOL": "False",
        "LYRICSTOOL": "False",
        "MEDIAINFOTOOL": "False",
        "MEDIASEGMENTSTOOL": "False",
        "MISCTOOL": "False",
        "MOVIESTOOL": "False",
        "MUSICGENRESTOOL": "False",
        "PACKAGETOOL": "False",
        "PERSONSTOOL": "False",
        "PLAYLISTSTOOL": "False",
        "PLAYSTATETOOL": "False",
        "PLUGINSTOOL": "False",
        "QUICKCONNECTTOOL": "False",
        "REMOTEIMAGETOOL": "False",
        "SCHEDULEDTASKSTOOL": "False",
        "SEARCHTOOL": "False",
        "SESSIONTOOL": "False",
        "STARTUPTOOL": "False",
        "STUDIOSTOOL": "False",
        "SUBTITLETOOL": "False",
        "SUGGESTIONSTOOL": "False",
        "SYNCPLAYTOOL": "False",
        "SYSTEMTOOL": "False",
        "TIMESYNCTOOL": "False",
        "TMDBTOOL": "False",
        "TRAILERSTOOL": "False",
        "TRICKPLAYTOOL": "False",
        "TVSHOWSTOOL": "False",
        "UNIVERSALAUDIOTOOL": "False",
        "USERLIBRARYTOOL": "False",
        "USERTOOL": "False",
        "USERVIEWSTOOL": "False",
        "VIDEOATTACHMENTSTOOL": "False",
        "VIDEOSTOOL": "False",
        "YEARSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/jellyfin-mcp.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command jellyfin-mcp \
    --enable-tag ACTIVITYLOGTOOL \
    --all-tags "ACTIVITYLOGTOOL,APIKEYTOOL,ARTISTSTOOL,AUDIOTOOL,BACKUPTOOL,BRANDINGTOOL,CHANNELSTOOL,CLIENTLOGTOOL,COLLECTIONTOOL,CONFIGURATIONTOOL,DASHBOARDTOOL,DEVICESTOOL,DISPLAYPREFERENCESTOOL,DYNAMICHLSTOOL,ENVIRONMENTTOOL,FILTERTOOL,GENRESTOOL,HLSSEGMENTTOOL,IMAGETOOL,INSTANTMIXTOOL,ITEMLOOKUPTOOL,ITEMREFRESHTOOL,ITEMSTOOL,ITEMUPDATETOOL,LIBRARYSTRUCTURETOOL,LIBRARYTOOL,LIVETVTOOL,LOCALIZATIONTOOL,LYRICSTOOL,MEDIAINFOTOOL,MEDIASEGMENTSTOOL,MISCTOOL,MOVIESTOOL,MUSICGENRESTOOL,PACKAGETOOL,PERSONSTOOL,PLAYLISTSTOOL,PLAYSTATETOOL,PLUGINSTOOL,QUICKCONNECTTOOL,REMOTEIMAGETOOL,SCHEDULEDTASKSTOOL,SEARCHTOOL,SESSIONTOOL,STARTUPTOOL,STUDIOSTOOL,SUBTITLETOOL,SUGGESTIONSTOOL,SYNCPLAYTOOL,SYSTEMTOOL,TIMESYNCTOOL,TMDBTOOL,TRAILERSTOOL,TRICKPLAYTOOL,TVSHOWSTOOL,UNIVERSALAUDIOTOOL,USERLIBRARYTOOL,USERTOOL,USERVIEWSTOOL,VIDEOATTACHMENTSTOOL,VIDEOSTOOL,YEARSTOOL"
```

## Tailored Skills Reference

### test-skill

**Description:** A test skill.

## test-skill Skill

### When to use
For testing.

### How to use
Call it.

### Examples
- Example 1: ...

### jellyfin-activity-log

**Description:** "Generated skill for ActivityLog operations. Contains 1 tools."

#### Overview
This skill handles operations related to ActivityLog.

#### Available Tools
- `get_log_entries_tool`: Gets activity log entries.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `min_date` (Optional[str])
    - `has_user_id` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-api-key

**Description:** "Generated skill for ApiKey operations. Contains 3 tools."

#### Overview
This skill handles operations related to ApiKey.

#### Available Tools
- `get_keys_tool`: Get all keys.
- `create_key_tool`: Create a new api key.
  - **Parameters**:
    - `app` (Optional[str])
- `revoke_key_tool`: Remove an api key.
  - **Parameters**:
    - `key` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-artists

**Description:** "Generated skill for Artists operations. Contains 3 tools."

#### Overview
This skill handles operations related to Artists.

#### Available Tools
- `get_artists_tool`: Gets all artists from a given item, folder, or the entire library.
  - **Parameters**:
    - `min_community_rating` (Optional[float])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `media_types` (Optional[List[Any]])
    - `genres` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `official_ratings` (Optional[List[Any]])
    - `tags` (Optional[List[Any]])
    - `years` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `person` (Optional[str])
    - `person_ids` (Optional[List[Any]])
    - `person_types` (Optional[List[Any]])
    - `studios` (Optional[List[Any]])
    - `studio_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_artist_by_name_tool`: Gets an artist by name.
  - **Parameters**:
    - `name` (str)
    - `user_id` (Optional[str])
- `get_album_artists_tool`: Gets all album artists from a given item, folder, or the entire library.
  - **Parameters**:
    - `min_community_rating` (Optional[float])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `media_types` (Optional[List[Any]])
    - `genres` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `official_ratings` (Optional[List[Any]])
    - `tags` (Optional[List[Any]])
    - `years` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `person` (Optional[str])
    - `person_ids` (Optional[List[Any]])
    - `person_types` (Optional[List[Any]])
    - `studios` (Optional[List[Any]])
    - `studio_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-audio

**Description:** "Generated skill for Audio operations. Contains 2 tools."

#### Overview
This skill handles operations related to Audio.

#### Available Tools
- `get_audio_stream_tool`: Gets an audio stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (Optional[str])
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `get_audio_stream_by_container_tool`: Gets an audio stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-backup

**Description:** "Generated skill for Backup operations. Contains 4 tools."

#### Overview
This skill handles operations related to Backup.

#### Available Tools
- `list_backups_tool`: Gets a list of all currently present backups in the backup directory.
- `create_backup_tool`: Creates a new Backup.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_backup_tool`: Gets the descriptor from an existing archive is present.
  - **Parameters**:
    - `path` (Optional[str])
- `start_restore_backup_tool`: Restores to a backup by restarting the server and applying the backup.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-branding

**Description:** "Generated skill for Branding operations. Contains 3 tools."

#### Overview
This skill handles operations related to Branding.

#### Available Tools
- `get_branding_options_tool`: Gets branding configuration.
- `get_branding_css_tool`: Gets branding css.
- `get_branding_css_2_tool`: Gets branding css.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-channels

**Description:** "Generated skill for Channels operations. Contains 5 tools."

#### Overview
This skill handles operations related to Channels.

#### Available Tools
- `get_channels_tool`: Gets available channels.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `supports_latest_items` (Optional[bool])
    - `supports_media_deletion` (Optional[bool])
    - `is_favorite` (Optional[bool])
- `get_channel_features_tool`: Get channel features.
  - **Parameters**:
    - `channel_id` (str)
- `get_channel_items_tool`: Get channel items.
  - **Parameters**:
    - `channel_id` (str)
    - `folder_id` (Optional[str])
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `sort_order` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `sort_by` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
- `get_all_channel_features_tool`: Get all channel features.
- `get_latest_channel_items_tool`: Gets latest channel items.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `filters` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
    - `channel_ids` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-client-log

**Description:** "Generated skill for ClientLog operations. Contains 1 tools."

#### Overview
This skill handles operations related to ClientLog.

#### Available Tools
- `log_file_tool`: Upload a document.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-collection

**Description:** "Generated skill for Collection operations. Contains 3 tools."

#### Overview
This skill handles operations related to Collection.

#### Available Tools
- `create_collection_tool`: Creates a new collection.
  - **Parameters**:
    - `name` (Optional[str])
    - `ids` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `is_locked` (Optional[bool])
- `add_to_collection_tool`: Adds items to a collection.
  - **Parameters**:
    - `collection_id` (str)
    - `ids` (Optional[List[Any]])
- `remove_from_collection_tool`: Removes items from a collection.
  - **Parameters**:
    - `collection_id` (str)
    - `ids` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-configuration

**Description:** "Generated skill for Configuration operations. Contains 6 tools."

#### Overview
This skill handles operations related to Configuration.

#### Available Tools
- `get_configuration_tool`: Gets application configuration.
- `update_configuration_tool`: Updates application configuration.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_named_configuration_tool`: Gets a named configuration.
  - **Parameters**:
    - `key` (str)
- `update_named_configuration_tool`: Updates named configuration.
  - **Parameters**:
    - `key` (str)
    - `body` (Optional[Dict[str, Any]])
- `update_branding_configuration_tool`: Updates branding configuration.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_default_metadata_options_tool`: Gets a default MetadataOptions object.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-dashboard

**Description:** "Generated skill for Dashboard operations. Contains 2 tools."

#### Overview
This skill handles operations related to Dashboard.

#### Available Tools
- `get_dashboard_configuration_page_tool`: Gets a dashboard configuration page.
  - **Parameters**:
    - `name` (Optional[str])
- `get_configuration_pages_tool`: Gets the configuration pages.
  - **Parameters**:
    - `enable_in_main_menu` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-devices

**Description:** "Generated skill for Devices operations. Contains 5 tools."

#### Overview
This skill handles operations related to Devices.

#### Available Tools
- `get_devices_tool`: Get Devices.
  - **Parameters**:
    - `user_id` (Optional[str])
- `delete_device_tool`: Deletes a device.
  - **Parameters**:
    - `id` (Optional[str])
- `get_device_info_tool`: Get info for a device.
  - **Parameters**:
    - `id` (Optional[str])
- `get_device_options_tool`: Get options for a device.
  - **Parameters**:
    - `id` (Optional[str])
- `update_device_options_tool`: Update device options.
  - **Parameters**:
    - `id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-display-preferences

**Description:** "Generated skill for DisplayPreferences operations. Contains 2 tools."

#### Overview
This skill handles operations related to DisplayPreferences.

#### Available Tools
- `get_display_preferences_tool`: Get Display Preferences.
  - **Parameters**:
    - `display_preferences_id` (str)
    - `user_id` (Optional[str])
    - `client` (Optional[str])
- `update_display_preferences_tool`: Update Display Preferences.
  - **Parameters**:
    - `display_preferences_id` (str)
    - `user_id` (Optional[str])
    - `client` (Optional[str])
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-dynamic-hls

**Description:** "Generated skill for DynamicHls operations. Contains 7 tools."

#### Overview
This skill handles operations related to DynamicHls.

#### Available Tools
- `get_hls_audio_segment_tool`: Gets a video stream using HTTP live streaming.
  - **Parameters**:
    - `item_id` (str)
    - `playlist_id` (str)
    - `segment_id` (int)
    - `container` (str)
    - `runtime_ticks` (Optional[int])
    - `actual_segment_length_ticks` (Optional[int])
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `max_streaming_bitrate` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `get_variant_hls_audio_playlist_tool`: Gets an audio stream using HTTP live streaming.
  - **Parameters**:
    - `item_id` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `max_streaming_bitrate` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `get_master_hls_audio_playlist_tool`: Gets an audio hls playlist stream.
  - **Parameters**:
    - `item_id` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `max_streaming_bitrate` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_adaptive_bitrate_streaming` (Optional[bool])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `get_hls_video_segment_tool`: Gets a video stream using HTTP live streaming.
  - **Parameters**:
    - `item_id` (str)
    - `playlist_id` (str)
    - `segment_id` (int)
    - `container` (str)
    - `runtime_ticks` (Optional[int])
    - `actual_segment_length_ticks` (Optional[int])
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
    - `always_burn_in_subtitle_when_transcoding` (Optional[bool])
- `get_live_hls_stream_tool`: Gets a hls live stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (Optional[str])
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `enable_subtitles_in_manifest` (Optional[bool])
    - `enable_audio_vbr_encoding` (Optional[bool])
    - `always_burn_in_subtitle_when_transcoding` (Optional[bool])
- `get_variant_hls_video_playlist_tool`: Gets a video stream using HTTP live streaming.
  - **Parameters**:
    - `item_id` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
    - `always_burn_in_subtitle_when_transcoding` (Optional[bool])
- `get_master_hls_video_playlist_tool`: Gets a video hls playlist stream.
  - **Parameters**:
    - `item_id` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_adaptive_bitrate_streaming` (Optional[bool])
    - `enable_trickplay` (Optional[bool])
    - `enable_audio_vbr_encoding` (Optional[bool])
    - `always_burn_in_subtitle_when_transcoding` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-environment

**Description:** "Generated skill for Environment operations. Contains 6 tools."

#### Overview
This skill handles operations related to Environment.

#### Available Tools
- `get_default_directory_browser_tool`: Get Default directory browser.
- `get_directory_contents_tool`: Gets the contents of a given directory in the file system.
  - **Parameters**:
    - `path` (Optional[str])
    - `include_files` (Optional[bool])
    - `include_directories` (Optional[bool])
- `get_drives_tool`: Gets available drives from the server's file system.
- `get_network_shares_tool`: Gets network paths.
- `get_parent_path_tool`: Gets the parent path of a given path.
  - **Parameters**:
    - `path` (Optional[str])
- `validate_path_tool`: Validates path.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-filter

**Description:** "Generated skill for Filter operations. Contains 2 tools."

#### Overview
This skill handles operations related to Filter.

#### Available Tools
- `get_query_filters_legacy_tool`: Gets legacy query filters.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `parent_id` (Optional[str])
    - `include_item_types` (Optional[List[Any]])
    - `media_types` (Optional[List[Any]])
- `get_query_filters_tool`: Gets query filters.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `parent_id` (Optional[str])
    - `include_item_types` (Optional[List[Any]])
    - `is_airing` (Optional[bool])
    - `is_movie` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_series` (Optional[bool])
    - `recursive` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-genres

**Description:** "Generated skill for Genres operations. Contains 2 tools."

#### Overview
This skill handles operations related to Genres.

#### Available Tools
- `get_genres_tool`: Gets all genres from a given item, folder, or the entire library.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_genre_tool`: Gets a genre, by name.
  - **Parameters**:
    - `genre_name` (str)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-hls-segment

**Description:** "Generated skill for HlsSegment operations. Contains 5 tools."

#### Overview
This skill handles operations related to HlsSegment.

#### Available Tools
- `get_hls_audio_segment_legacy_aac_tool`: Gets the specified audio segment for an audio item.
  - **Parameters**:
    - `item_id` (str)
    - `segment_id` (str)
- `get_hls_audio_segment_legacy_mp3_tool`: Gets the specified audio segment for an audio item.
  - **Parameters**:
    - `item_id` (str)
    - `segment_id` (str)
- `get_hls_video_segment_legacy_tool`: Gets a hls video segment.
  - **Parameters**:
    - `item_id` (str)
    - `playlist_id` (str)
    - `segment_id` (str)
    - `segment_container` (str)
- `get_hls_playlist_legacy_tool`: Gets a hls video playlist.
  - **Parameters**:
    - `item_id` (str)
    - `playlist_id` (str)
- `stop_encoding_process_tool`: Stops an active encoding.
  - **Parameters**:
    - `device_id` (Optional[str])
    - `play_session_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-image

**Description:** "Generated skill for Image operations. Contains 24 tools."

#### Overview
This skill handles operations related to Image.

#### Available Tools
- `get_artist_image_tool`: Get artist image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `get_splashscreen_tool`: Generates or gets the splashscreen.
  - **Parameters**:
    - `tag` (Optional[str])
    - `format` (Optional[str])
- `upload_custom_splashscreen_tool`: Uploads a custom splashscreen. The body is expected to the image contents base64 encoded.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `delete_custom_splashscreen_tool`: Delete a custom splashscreen.
- `get_genre_image_tool`: Get genre image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
    - `image_index` (Optional[int])
- `get_genre_image_by_index_tool`: Get genre image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `get_item_image_infos_tool`: Get item image infos.
  - **Parameters**:
    - `item_id` (str)
- `delete_item_image_tool`: Delete an item's image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `image_index` (Optional[int])
- `set_item_image_tool`: Set item image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `body` (Optional[Dict[str, Any]])
- `get_item_image_tool`: Gets the item's image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
    - `image_index` (Optional[int])
- `delete_item_image_by_index_tool`: Delete an item's image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `image_index` (int)
- `set_item_image_by_index_tool`: Set item image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `body` (Optional[Dict[str, Any]])
- `get_item_image_by_index_tool`: Gets the item's image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `get_item_image2_tool`: Gets the item's image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `max_width` (int)
    - `max_height` (int)
    - `tag` (str)
    - `format` (str)
    - `percent_played` (float)
    - `unplayed_count` (int)
    - `image_index` (int)
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `update_item_image_index_tool`: Updates the index for an item image.
  - **Parameters**:
    - `item_id` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `new_index` (Optional[int])
- `get_music_genre_image_tool`: Get music genre image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
    - `image_index` (Optional[int])
- `get_music_genre_image_by_index_tool`: Get music genre image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `get_person_image_tool`: Get person image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
    - `image_index` (Optional[int])
- `get_person_image_by_index_tool`: Get person image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `get_studio_image_tool`: Get studio image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
    - `image_index` (Optional[int])
- `get_studio_image_by_index_tool`: Get studio image by name.
  - **Parameters**:
    - `name` (str)
    - `image_type` (str)
    - `image_index` (int)
    - `tag` (Optional[str])
    - `format` (Optional[str])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `percent_played` (Optional[float])
    - `unplayed_count` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `quality` (Optional[int])
    - `fill_width` (Optional[int])
    - `fill_height` (Optional[int])
    - `blur` (Optional[int])
    - `background_color` (Optional[str])
    - `foreground_layer` (Optional[str])
- `post_user_image_tool`: Sets the user image.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `delete_user_image_tool`: Delete the user's image.
  - **Parameters**:
    - `user_id` (Optional[str])
- `get_user_image_tool`: Get user profile image.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `tag` (Optional[str])
    - `format` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-instant-mix

**Description:** "Generated skill for InstantMix operations. Contains 8 tools."

#### Overview
This skill handles operations related to InstantMix.

#### Available Tools
- `get_instant_mix_from_album_tool`: Creates an instant playlist based on a given album.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_artists_tool`: Creates an instant playlist based on a given artist.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_artists2_tool`: Creates an instant playlist based on a given artist.
  - **Parameters**:
    - `id` (Optional[str])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_item_tool`: Creates an instant playlist based on a given item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_music_genre_by_name_tool`: Creates an instant playlist based on a given genre.
  - **Parameters**:
    - `name` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_music_genre_by_id_tool`: Creates an instant playlist based on a given genre.
  - **Parameters**:
    - `id` (Optional[str])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_playlist_tool`: Creates an instant playlist based on a given playlist.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `get_instant_mix_from_song_tool`: Creates an instant playlist based on a given song.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-item-lookup

**Description:** "Generated skill for ItemLookup operations. Contains 11 tools."

#### Overview
This skill handles operations related to ItemLookup.

#### Available Tools
- `get_external_id_infos_tool`: Get the item's external id info.
  - **Parameters**:
    - `item_id` (str)
- `apply_search_criteria_tool`: Applies search criteria to an item and refreshes metadata.
  - **Parameters**:
    - `item_id` (str)
    - `replace_all_images` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `get_book_remote_search_results_tool`: Get book remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_box_set_remote_search_results_tool`: Get box set remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_movie_remote_search_results_tool`: Get movie remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_music_album_remote_search_results_tool`: Get music album remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_music_artist_remote_search_results_tool`: Get music artist remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_music_video_remote_search_results_tool`: Get music video remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_person_remote_search_results_tool`: Get person remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_series_remote_search_results_tool`: Get series remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_trailer_remote_search_results_tool`: Get trailer remote search.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-item-refresh

**Description:** "Generated skill for ItemRefresh operations. Contains 1 tools."

#### Overview
This skill handles operations related to ItemRefresh.

#### Available Tools
- `refresh_item_tool`: Refreshes metadata for an item.
  - **Parameters**:
    - `item_id` (str)
    - `metadata_refresh_mode` (Optional[str])
    - `image_refresh_mode` (Optional[str])
    - `replace_all_metadata` (Optional[bool])
    - `replace_all_images` (Optional[bool])
    - `regenerate_trickplay` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-item-update

**Description:** "Generated skill for ItemUpdate operations. Contains 3 tools."

#### Overview
This skill handles operations related to ItemUpdate.

#### Available Tools
- `update_item_tool`: Updates an item.
  - **Parameters**:
    - `item_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `update_item_content_type_tool`: Updates an item's content type.
  - **Parameters**:
    - `item_id` (str)
    - `content_type` (Optional[str])
- `get_metadata_editor_info_tool`: Gets metadata editor info for an item.
  - **Parameters**:
    - `item_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-items

**Description:** "Generated skill for Items operations. Contains 4 tools."

#### Overview
This skill handles operations related to Items.

#### Available Tools
- `get_items_tool`: Gets items based on a query.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `max_official_rating` (Optional[str])
    - `has_theme_song` (Optional[bool])
    - `has_theme_video` (Optional[bool])
    - `has_subtitles` (Optional[bool])
    - `has_special_feature` (Optional[bool])
    - `has_trailer` (Optional[bool])
    - `adjacent_to` (Optional[str])
    - `index_number` (Optional[int])
    - `parent_index_number` (Optional[int])
    - `has_parental_rating` (Optional[bool])
    - `is_hd` (Optional[bool])
    - `is4_k` (Optional[bool])
    - `location_types` (Optional[List[Any]])
    - `exclude_location_types` (Optional[List[Any]])
    - `is_missing` (Optional[bool])
    - `is_unaired` (Optional[bool])
    - `min_community_rating` (Optional[float])
    - `min_critic_rating` (Optional[float])
    - `min_premiere_date` (Optional[str])
    - `min_date_last_saved` (Optional[str])
    - `min_date_last_saved_for_user` (Optional[str])
    - `max_premiere_date` (Optional[str])
    - `has_overview` (Optional[bool])
    - `has_imdb_id` (Optional[bool])
    - `has_tmdb_id` (Optional[bool])
    - `has_tvdb_id` (Optional[bool])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `exclude_item_ids` (Optional[List[Any]])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `recursive` (Optional[bool])
    - `search_term` (Optional[str])
    - `sort_order` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `media_types` (Optional[List[Any]])
    - `image_types` (Optional[List[Any]])
    - `sort_by` (Optional[List[Any]])
    - `is_played` (Optional[bool])
    - `genres` (Optional[List[Any]])
    - `official_ratings` (Optional[List[Any]])
    - `tags` (Optional[List[Any]])
    - `years` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `person` (Optional[str])
    - `person_ids` (Optional[List[Any]])
    - `person_types` (Optional[List[Any]])
    - `studios` (Optional[List[Any]])
    - `artists` (Optional[List[Any]])
    - `exclude_artist_ids` (Optional[List[Any]])
    - `artist_ids` (Optional[List[Any]])
    - `album_artist_ids` (Optional[List[Any]])
    - `contributing_artist_ids` (Optional[List[Any]])
    - `albums` (Optional[List[Any]])
    - `album_ids` (Optional[List[Any]])
    - `ids` (Optional[List[Any]])
    - `video_types` (Optional[List[Any]])
    - `min_official_rating` (Optional[str])
    - `is_locked` (Optional[bool])
    - `is_place_holder` (Optional[bool])
    - `has_official_rating` (Optional[bool])
    - `collapse_box_set_items` (Optional[bool])
    - `min_width` (Optional[int])
    - `min_height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `is3_d` (Optional[bool])
    - `series_status` (Optional[List[Any]])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `studio_ids` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `enable_total_record_count` (Optional[bool])
    - `enable_images` (Optional[bool])
- `get_item_user_data_tool`: Get Item User Data.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `update_item_user_data_tool`: Update Item User Data.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `get_resume_items_tool`: Gets items based on a query.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `media_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `enable_total_record_count` (Optional[bool])
    - `enable_images` (Optional[bool])
    - `exclude_active_sessions` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-library-structure

**Description:** "Generated skill for LibraryStructure operations. Contains 8 tools."

#### Overview
This skill handles operations related to LibraryStructure.

#### Available Tools
- `get_virtual_folders_tool`: Gets all virtual folders.
- `add_virtual_folder_tool`: Adds a virtual folder.
  - **Parameters**:
    - `name` (Optional[str])
    - `collection_type` (Optional[str])
    - `paths` (Optional[List[Any]])
    - `refresh_library` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `remove_virtual_folder_tool`: Removes a virtual folder.
  - **Parameters**:
    - `name` (Optional[str])
    - `refresh_library` (Optional[bool])
- `update_library_options_tool`: Update library options.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `rename_virtual_folder_tool`: Renames a virtual folder.
  - **Parameters**:
    - `name` (Optional[str])
    - `new_name` (Optional[str])
    - `refresh_library` (Optional[bool])
- `add_media_path_tool`: Add a media path to a library.
  - **Parameters**:
    - `refresh_library` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `remove_media_path_tool`: Remove a media path.
  - **Parameters**:
    - `name` (Optional[str])
    - `path` (Optional[str])
    - `refresh_library` (Optional[bool])
- `update_media_path_tool`: Updates a media path.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-library

**Description:** "Generated skill for Library operations. Contains 25 tools."

#### Overview
This skill handles operations related to Library.

#### Available Tools
- `delete_items_tool`: Deletes items from the library and filesystem.
  - **Parameters**:
    - `ids` (Optional[List[Any]])
- `delete_item_tool`: Deletes an item from the library and filesystem.
  - **Parameters**:
    - `item_id` (str)
- `get_similar_albums_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
- `get_similar_artists_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
- `get_ancestors_tool`: Gets all parents of an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_critic_reviews_tool`: Gets critic review for an item.
  - **Parameters**:
    - `item_id` (str)
- `get_download_tool`: Downloads item media.
  - **Parameters**:
    - `item_id` (str)
- `get_file_tool`: Get the original file of an item.
  - **Parameters**:
    - `item_id` (str)
- `get_similar_items_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
- `get_theme_media_tool`: Get theme songs and videos for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `inherit_from_parent` (Optional[bool])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
- `get_theme_songs_tool`: Get theme songs for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `inherit_from_parent` (Optional[bool])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
- `get_theme_videos_tool`: Get theme videos for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `inherit_from_parent` (Optional[bool])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
- `get_item_counts_tool`: Get item counts.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `is_favorite` (Optional[bool])
- `get_library_options_info_tool`: Gets the library options info.
  - **Parameters**:
    - `library_content_type` (Optional[str])
    - `is_new_library` (Optional[bool])
- `post_updated_media_tool`: Reports that new movies have been added by an external source.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_media_folders_tool`: Gets all user media folders.
  - **Parameters**:
    - `is_hidden` (Optional[bool])
- `post_added_movies_tool`: Reports that new movies have been added by an external source.
  - **Parameters**:
    - `tmdb_id` (Optional[str])
    - `imdb_id` (Optional[str])
- `post_updated_movies_tool`: Reports that new movies have been added by an external source.
  - **Parameters**:
    - `tmdb_id` (Optional[str])
    - `imdb_id` (Optional[str])
- `get_physical_paths_tool`: Gets a list of physical paths from virtual folders.
- `refresh_library_tool`: Starts a library scan.
- `post_added_series_tool`: Reports that new episodes of a series have been added by an external source.
  - **Parameters**:
    - `tvdb_id` (Optional[str])
- `post_updated_series_tool`: Reports that new episodes of a series have been added by an external source.
  - **Parameters**:
    - `tvdb_id` (Optional[str])
- `get_similar_movies_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
- `get_similar_shows_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
- `get_similar_trailers_tool`: Gets similar items.
  - **Parameters**:
    - `item_id` (str)
    - `exclude_artist_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-live-tv

**Description:** "Generated skill for LiveTv operations. Contains 41 tools."

#### Overview
This skill handles operations related to LiveTv.

#### Available Tools
- `get_channel_mapping_options_tool`: Get channel mapping options.
  - **Parameters**:
    - `provider_id` (Optional[str])
- `set_channel_mapping_tool`: Set channel mappings.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_live_tv_channels_tool`: Gets available live tv channels.
  - **Parameters**:
    - `type` (Optional[str])
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `limit` (Optional[int])
    - `is_favorite` (Optional[bool])
    - `is_liked` (Optional[bool])
    - `is_disliked` (Optional[bool])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[str])
    - `enable_favorite_sorting` (Optional[bool])
    - `add_current_program` (Optional[bool])
- `get_channel_tool`: Gets a live tv channel.
  - **Parameters**:
    - `channel_id` (str)
    - `user_id` (Optional[str])
- `get_guide_info_tool`: Get guide info.
- `get_live_tv_info_tool`: Gets available live tv services.
- `add_listing_provider_tool`: Adds a listings provider.
  - **Parameters**:
    - `pw` (Optional[str])
    - `validate_listings` (Optional[bool])
    - `validate_login` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `delete_listing_provider_tool`: Delete listing provider.
  - **Parameters**:
    - `id` (Optional[str])
- `get_default_listing_provider_tool`: Gets default listings provider info.
- `get_lineups_tool`: Gets available lineups.
  - **Parameters**:
    - `id` (Optional[str])
    - `type` (Optional[str])
    - `location` (Optional[str])
    - `country` (Optional[str])
- `get_schedules_direct_countries_tool`: Gets available countries.
- `get_live_recording_file_tool`: Gets a live tv recording stream.
  - **Parameters**:
    - `recording_id` (str)
- `get_live_stream_file_tool`: Gets a live tv channel stream.
  - **Parameters**:
    - `stream_id` (str)
    - `container` (str)
- `get_live_tv_programs_tool`: Gets available live tv epgs.
  - **Parameters**:
    - `channel_ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `min_start_date` (Optional[str])
    - `has_aired` (Optional[bool])
    - `is_airing` (Optional[bool])
    - `max_start_date` (Optional[str])
    - `min_end_date` (Optional[str])
    - `max_end_date` (Optional[str])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
    - `genres` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `series_timer_id` (Optional[str])
    - `library_series_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `enable_total_record_count` (Optional[bool])
- `get_programs_tool`: Gets available live tv epgs.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_program_tool`: Gets a live tv program.
  - **Parameters**:
    - `program_id` (str)
    - `user_id` (Optional[str])
- `get_recommended_programs_tool`: Gets recommended live tv epgs.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `is_airing` (Optional[bool])
    - `has_aired` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_movie` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_recordings_tool`: Gets live tv recordings.
  - **Parameters**:
    - `channel_id` (Optional[str])
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `status` (Optional[str])
    - `is_in_progress` (Optional[bool])
    - `series_timer_id` (Optional[str])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_library_item` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_recording_tool`: Gets a live tv recording.
  - **Parameters**:
    - `recording_id` (str)
    - `user_id` (Optional[str])
- `delete_recording_tool`: Deletes a live tv recording.
  - **Parameters**:
    - `recording_id` (str)
- `get_recording_folders_tool`: Gets recording folders.
  - **Parameters**:
    - `user_id` (Optional[str])
- `get_recording_groups_tool`: Gets live tv recording groups.
  - **Parameters**:
    - `user_id` (Optional[str])
- `get_recording_group_tool`: Get recording group.
  - **Parameters**:
    - `group_id` (str)
- `get_recordings_series_tool`: Gets live tv recording series.
  - **Parameters**:
    - `channel_id` (Optional[str])
    - `user_id` (Optional[str])
    - `group_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `status` (Optional[str])
    - `is_in_progress` (Optional[bool])
    - `series_timer_id` (Optional[str])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `fields` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_series_timers_tool`: Gets live tv series timers.
  - **Parameters**:
    - `sort_by` (Optional[str])
    - `sort_order` (Optional[str])
- `create_series_timer_tool`: Creates a live tv series timer.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_series_timer_tool`: Gets a live tv series timer.
  - **Parameters**:
    - `timer_id` (str)
- `cancel_series_timer_tool`: Cancels a live tv series timer.
  - **Parameters**:
    - `timer_id` (str)
- `update_series_timer_tool`: Updates a live tv series timer.
  - **Parameters**:
    - `timer_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `get_timers_tool`: Gets the live tv timers.
  - **Parameters**:
    - `channel_id` (Optional[str])
    - `series_timer_id` (Optional[str])
    - `is_active` (Optional[bool])
    - `is_scheduled` (Optional[bool])
- `create_timer_tool`: Creates a live tv timer.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_timer_tool`: Gets a timer.
  - **Parameters**:
    - `timer_id` (str)
- `cancel_timer_tool`: Cancels a live tv timer.
  - **Parameters**:
    - `timer_id` (str)
- `update_timer_tool`: Updates a live tv timer.
  - **Parameters**:
    - `timer_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `get_default_timer_tool`: Gets the default values for a new timer.
  - **Parameters**:
    - `program_id` (Optional[str])
- `add_tuner_host_tool`: Adds a tuner host.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `delete_tuner_host_tool`: Deletes a tuner host.
  - **Parameters**:
    - `id` (Optional[str])
- `get_tuner_host_types_tool`: Get tuner host types.
- `reset_tuner_tool`: Resets a tv tuner.
  - **Parameters**:
    - `tuner_id` (str)
- `discover_tuners_tool`: Discover tuners.
  - **Parameters**:
    - `new_devices_only` (Optional[bool])
- `discvover_tuners_tool`: Discover tuners.
  - **Parameters**:
    - `new_devices_only` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-localization

**Description:** "Generated skill for Localization operations. Contains 4 tools."

#### Overview
This skill handles operations related to Localization.

#### Available Tools
- `get_countries_tool`: Gets known countries.
- `get_cultures_tool`: Gets known cultures.
- `get_localization_options_tool`: Gets localization options.
- `get_parental_ratings_tool`: Gets known parental ratings.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-lyrics

**Description:** "Generated skill for Lyrics operations. Contains 6 tools."

#### Overview
This skill handles operations related to Lyrics.

#### Available Tools
- `get_lyrics_tool`: Gets an item's lyrics.
  - **Parameters**:
    - `item_id` (str)
- `upload_lyrics_tool`: Upload an external lyric file.
  - **Parameters**:
    - `item_id` (str)
    - `file_name` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `delete_lyrics_tool`: Deletes an external lyric file.
  - **Parameters**:
    - `item_id` (str)
- `search_remote_lyrics_tool`: Search remote lyrics.
  - **Parameters**:
    - `item_id` (str)
- `download_remote_lyrics_tool`: Downloads a remote lyric.
  - **Parameters**:
    - `item_id` (str)
    - `lyric_id` (str)
- `get_remote_lyrics_tool`: Gets the remote lyrics.
  - **Parameters**:
    - `lyric_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-media-info

**Description:** "Generated skill for MediaInfo operations. Contains 5 tools."

#### Overview
This skill handles operations related to MediaInfo.

#### Available Tools
- `get_playback_info_tool`: Gets live playback media info for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_posted_playback_info_tool`: Gets live playback media info for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `max_streaming_bitrate` (Optional[int])
    - `start_time_ticks` (Optional[int])
    - `audio_stream_index` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `media_source_id` (Optional[str])
    - `live_stream_id` (Optional[str])
    - `auto_open_live_stream` (Optional[bool])
    - `enable_direct_play` (Optional[bool])
    - `enable_direct_stream` (Optional[bool])
    - `enable_transcoding` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `close_live_stream_tool`: Closes a media source.
  - **Parameters**:
    - `live_stream_id` (Optional[str])
- `open_live_stream_tool`: Opens a media source.
  - **Parameters**:
    - `open_token` (Optional[str])
    - `user_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `max_streaming_bitrate` (Optional[int])
    - `start_time_ticks` (Optional[int])
    - `audio_stream_index` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `item_id` (Optional[str])
    - `enable_direct_play` (Optional[bool])
    - `enable_direct_stream` (Optional[bool])
    - `always_burn_in_subtitle_when_transcoding` (Optional[bool])
    - `body` (Optional[Dict[str, Any]])
- `get_bitrate_test_bytes_tool`: Tests the network with a request with the size of the bitrate.
  - **Parameters**:
    - `size` (Optional[int])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-media-segments

**Description:** "Generated skill for MediaSegments operations. Contains 1 tools."

#### Overview
This skill handles operations related to MediaSegments.

#### Available Tools
- `get_item_segments_tool`: Gets all media segments based on an itemId.
  - **Parameters**:
    - `item_id` (str)
    - `include_segment_types` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-movies

**Description:** "Generated skill for Movies operations. Contains 1 tools."

#### Overview
This skill handles operations related to Movies.

#### Available Tools
- `get_movie_recommendations_tool`: Gets movie recommendations.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `category_limit` (Optional[int])
    - `item_limit` (Optional[int])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-music-genres

**Description:** "Generated skill for MusicGenres operations. Contains 2 tools."

#### Overview
This skill handles operations related to MusicGenres.

#### Available Tools
- `get_music_genres_tool`: Gets all music genres from a given item, folder, or the entire library.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `sort_by` (Optional[List[Any]])
    - `sort_order` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_music_genre_tool`: Gets a music genre, by name.
  - **Parameters**:
    - `genre_name` (str)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-package

**Description:** "Generated skill for Package operations. Contains 6 tools."

#### Overview
This skill handles operations related to Package.

#### Available Tools
- `get_packages_tool`: Gets available packages.
- `get_package_info_tool`: Gets a package by name or assembly GUID.
  - **Parameters**:
    - `name` (str)
    - `assembly_guid` (Optional[str])
- `install_package_tool`: Installs a package.
  - **Parameters**:
    - `name` (str)
    - `assembly_guid` (Optional[str])
    - `version` (Optional[str])
    - `repository_url` (Optional[str])
- `cancel_package_installation_tool`: Cancels a package installation.
  - **Parameters**:
    - `package_id` (str)
- `get_repositories_tool`: Gets all package repositories.
- `set_repositories_tool`: Sets the enabled and existing package repositories.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-persons

**Description:** "Generated skill for Persons operations. Contains 2 tools."

#### Overview
This skill handles operations related to Persons.

#### Available Tools
- `get_persons_tool`: Gets all persons.
  - **Parameters**:
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `exclude_person_types` (Optional[List[Any]])
    - `person_types` (Optional[List[Any]])
    - `appears_in_item_id` (Optional[str])
    - `user_id` (Optional[str])
    - `enable_images` (Optional[bool])
- `get_person_tool`: Get person by name.
  - **Parameters**:
    - `name` (str)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-playlists

**Description:** "Generated skill for Playlists operations. Contains 11 tools."

#### Overview
This skill handles operations related to Playlists.

#### Available Tools
- `create_playlist_tool`: Creates a new playlist.
  - **Parameters**:
    - `name` (Optional[str])
    - `ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `media_type` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `update_playlist_tool`: Updates a playlist.
  - **Parameters**:
    - `playlist_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `get_playlist_tool`: Get a playlist.
  - **Parameters**:
    - `playlist_id` (str)
- `add_item_to_playlist_tool`: Adds items to a playlist.
  - **Parameters**:
    - `playlist_id` (str)
    - `ids` (Optional[List[Any]])
    - `user_id` (Optional[str])
- `remove_item_from_playlist_tool`: Removes items from a playlist.
  - **Parameters**:
    - `playlist_id` (str)
    - `entry_ids` (Optional[List[Any]])
- `get_playlist_items_tool`: Gets the original items of a playlist.
  - **Parameters**:
    - `playlist_id` (str)
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `enable_images` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
- `move_item_tool`: Moves a playlist item.
  - **Parameters**:
    - `playlist_id` (str)
    - `item_id` (str)
    - `new_index` (int)
- `get_playlist_users_tool`: Get a playlist's users.
  - **Parameters**:
    - `playlist_id` (str)
- `get_playlist_user_tool`: Get a playlist user.
  - **Parameters**:
    - `playlist_id` (str)
    - `user_id` (str)
- `update_playlist_user_tool`: Modify a user of a playlist's users.
  - **Parameters**:
    - `playlist_id` (str)
    - `user_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `remove_user_from_playlist_tool`: Remove a user from a playlist's users.
  - **Parameters**:
    - `playlist_id` (str)
    - `user_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-playstate

**Description:** "Generated skill for Playstate operations. Contains 9 tools."

#### Overview
This skill handles operations related to Playstate.

#### Available Tools
- `on_playback_start_tool`: Reports that a session has begun playing an item.
  - **Parameters**:
    - `item_id` (str)
    - `media_source_id` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `play_method` (Optional[str])
    - `live_stream_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `can_seek` (Optional[bool])
- `on_playback_stopped_tool`: Reports that a session has stopped playing an item.
  - **Parameters**:
    - `item_id` (str)
    - `media_source_id` (Optional[str])
    - `next_media_type` (Optional[str])
    - `position_ticks` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `play_session_id` (Optional[str])
- `on_playback_progress_tool`: Reports a session's playback progress.
  - **Parameters**:
    - `item_id` (str)
    - `media_source_id` (Optional[str])
    - `position_ticks` (Optional[int])
    - `audio_stream_index` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `volume_level` (Optional[int])
    - `play_method` (Optional[str])
    - `live_stream_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `repeat_mode` (Optional[str])
    - `is_paused` (Optional[bool])
    - `is_muted` (Optional[bool])
- `report_playback_start_tool`: Reports playback has started within a session.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `ping_playback_session_tool`: Pings a playback session.
  - **Parameters**:
    - `play_session_id` (Optional[str])
- `report_playback_progress_tool`: Reports playback progress within a session.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `report_playback_stopped_tool`: Reports playback has stopped within a session.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `mark_played_item_tool`: Marks an item as played for user.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `date_played` (Optional[str])
- `mark_unplayed_item_tool`: Marks an item as unplayed for user.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-plugins

**Description:** "Generated skill for Plugins operations. Contains 9 tools."

#### Overview
This skill handles operations related to Plugins.

#### Available Tools
- `get_plugins_tool`: Gets a list of currently installed plugins.
- `uninstall_plugin_tool`: Uninstalls a plugin.
  - **Parameters**:
    - `plugin_id` (str)
- `uninstall_plugin_by_version_tool`: Uninstalls a plugin by version.
  - **Parameters**:
    - `plugin_id` (str)
    - `version` (str)
- `disable_plugin_tool`: Disable a plugin.
  - **Parameters**:
    - `plugin_id` (str)
    - `version` (str)
- `enable_plugin_tool`: Enables a disabled plugin.
  - **Parameters**:
    - `plugin_id` (str)
    - `version` (str)
- `get_plugin_image_tool`: Gets a plugin's image.
  - **Parameters**:
    - `plugin_id` (str)
    - `version` (str)
- `get_plugin_configuration_tool`: Gets plugin configuration.
  - **Parameters**:
    - `plugin_id` (str)
- `update_plugin_configuration_tool`: Updates plugin configuration.
  - **Parameters**:
    - `plugin_id` (str)
- `get_plugin_manifest_tool`: Gets a plugin's manifest.
  - **Parameters**:
    - `plugin_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-quick-connect

**Description:** "Generated skill for QuickConnect operations. Contains 4 tools."

#### Overview
This skill handles operations related to QuickConnect.

#### Available Tools
- `authorize_quick_connect_tool`: Authorizes a pending quick connect request.
  - **Parameters**:
    - `code` (Optional[str])
    - `user_id` (Optional[str])
- `get_quick_connect_state_tool`: Attempts to retrieve authentication information.
  - **Parameters**:
    - `secret` (Optional[str])
- `get_quick_connect_enabled_tool`: Gets the current quick connect state.
- `initiate_quick_connect_tool`: Initiate a new quick connect request.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-remote-image

**Description:** "Generated skill for RemoteImage operations. Contains 3 tools."

#### Overview
This skill handles operations related to RemoteImage.

#### Available Tools
- `get_remote_images_tool`: Gets available remote images for an item.
  - **Parameters**:
    - `item_id` (str)
    - `type` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `provider_name` (Optional[str])
    - `include_all_languages` (Optional[bool])
- `download_remote_image_tool`: Downloads a remote image for an item.
  - **Parameters**:
    - `item_id` (str)
    - `type` (Optional[str])
    - `image_url` (Optional[str])
- `get_remote_image_providers_tool`: Gets available remote image providers for an item.
  - **Parameters**:
    - `item_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-scheduled-tasks

**Description:** "Generated skill for ScheduledTasks operations. Contains 5 tools."

#### Overview
This skill handles operations related to ScheduledTasks.

#### Available Tools
- `get_tasks_tool`: Get tasks.
  - **Parameters**:
    - `is_hidden` (Optional[bool])
    - `is_enabled` (Optional[bool])
- `get_task_tool`: Get task by id.
  - **Parameters**:
    - `task_id` (str)
- `update_task_tool`: Update specified task triggers.
  - **Parameters**:
    - `task_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `start_task_tool`: Start specified task.
  - **Parameters**:
    - `task_id` (str)
- `stop_task_tool`: Stop specified task.
  - **Parameters**:
    - `task_id` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-search

**Description:** "Generated skill for Search operations. Contains 1 tools."

#### Overview
This skill handles operations related to Search.

#### Available Tools
- `get_search_hints_tool`: Gets the search hint result.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `user_id` (Optional[str])
    - `search_term` (Optional[str])
    - `include_item_types` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `media_types` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `include_people` (Optional[bool])
    - `include_media` (Optional[bool])
    - `include_genres` (Optional[bool])
    - `include_studios` (Optional[bool])
    - `include_artists` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-session

**Description:** "Generated skill for Session operations. Contains 16 tools."

#### Overview
This skill handles operations related to Session.

#### Available Tools
- `get_password_reset_providers_tool`: Get all password reset providers.
- `get_auth_providers_tool`: Get all auth providers.
- `get_sessions_tool`: Gets a list of sessions.
  - **Parameters**:
    - `controllable_by_user_id` (Optional[str])
    - `device_id` (Optional[str])
    - `active_within_seconds` (Optional[int])
- `send_full_general_command_tool`: Issues a full general command to a client.
  - **Parameters**:
    - `session_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `send_general_command_tool`: Issues a general command to a client.
  - **Parameters**:
    - `session_id` (str)
    - `command` (str)
- `send_message_command_tool`: Issues a command to a client to display a message to the user.
  - **Parameters**:
    - `session_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `play_tool`: Instructs a session to play an item.
  - **Parameters**:
    - `session_id` (str)
    - `play_command` (Optional[str])
    - `item_ids` (Optional[List[Any]])
    - `start_position_ticks` (Optional[int])
    - `media_source_id` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `start_index` (Optional[int])
- `send_playstate_command_tool`: Issues a playstate command to a client.
  - **Parameters**:
    - `session_id` (str)
    - `command` (str)
    - `seek_position_ticks` (Optional[int])
    - `controlling_user_id` (Optional[str])
- `send_system_command_tool`: Issues a system command to a client.
  - **Parameters**:
    - `session_id` (str)
    - `command` (str)
- `add_user_to_session_tool`: Adds an additional user to a session.
  - **Parameters**:
    - `session_id` (str)
    - `user_id` (str)
- `remove_user_from_session_tool`: Removes an additional user from a session.
  - **Parameters**:
    - `session_id` (str)
    - `user_id` (str)
- `display_content_tool`: Instructs a session to browse to an item or view.
  - **Parameters**:
    - `session_id` (str)
    - `item_type` (Optional[str])
    - `item_id` (Optional[str])
    - `item_name` (Optional[str])
- `post_capabilities_tool`: Updates capabilities for a device.
  - **Parameters**:
    - `id` (Optional[str])
    - `playable_media_types` (Optional[List[Any]])
    - `supported_commands` (Optional[List[Any]])
    - `supports_media_control` (Optional[bool])
    - `supports_persistent_identifier` (Optional[bool])
- `post_full_capabilities_tool`: Updates capabilities for a device.
  - **Parameters**:
    - `id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `report_session_ended_tool`: Reports that a session has ended.
- `report_viewing_tool`: Reports that a session is viewing an item.
  - **Parameters**:
    - `session_id` (Optional[str])
    - `item_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-startup

**Description:** "Generated skill for Startup operations. Contains 7 tools."

#### Overview
This skill handles operations related to Startup.

#### Available Tools
- `complete_wizard_tool`: Completes the startup wizard.
- `get_startup_configuration_tool`: Gets the initial startup wizard configuration.
- `update_initial_configuration_tool`: Sets the initial startup wizard configuration.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_first_user_2_tool`: Gets the first user.
- `set_remote_access_tool`: Sets remote access and UPnP.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_first_user_tool`: Gets the first user.
- `update_startup_user_tool`: Sets the user name and password.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-studios

**Description:** "Generated skill for Studios operations. Contains 2 tools."

#### Overview
This skill handles operations related to Studios.

#### Available Tools
- `get_studios_tool`: Gets all studios from a given item, folder, or the entire library.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `search_term` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `enable_images` (Optional[bool])
    - `enable_total_record_count` (Optional[bool])
- `get_studio_tool`: Gets a studio by name.
  - **Parameters**:
    - `name` (str)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-subtitle

**Description:** "Generated skill for Subtitle operations. Contains 10 tools."

#### Overview
This skill handles operations related to Subtitle.

#### Available Tools
- `get_fallback_font_list_tool`: Gets a list of available fallback font files.
- `get_fallback_font_tool`: Gets a fallback font file.
  - **Parameters**:
    - `name` (str)
- `search_remote_subtitles_tool`: Search remote subtitles.
  - **Parameters**:
    - `item_id` (str)
    - `language` (str)
    - `is_perfect_match` (Optional[bool])
- `download_remote_subtitles_tool`: Downloads a remote subtitle.
  - **Parameters**:
    - `item_id` (str)
    - `subtitle_id` (str)
- `get_remote_subtitles_tool`: Gets the remote subtitles.
  - **Parameters**:
    - `subtitle_id` (str)
- `get_subtitle_playlist_tool`: Gets an HLS subtitle playlist.
  - **Parameters**:
    - `item_id` (str)
    - `index` (int)
    - `media_source_id` (str)
    - `segment_length` (Optional[int])
- `upload_subtitle_tool`: Upload an external subtitle file.
  - **Parameters**:
    - `item_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `delete_subtitle_tool`: Deletes an external subtitle file.
  - **Parameters**:
    - `item_id` (str)
    - `index` (int)
- `get_subtitle_with_ticks_tool`: Gets subtitles in a specified format.
  - **Parameters**:
    - `route_item_id` (str)
    - `route_media_source_id` (str)
    - `route_index` (int)
    - `route_start_position_ticks` (int)
    - `route_format` (str)
    - `item_id` (Optional[str])
    - `media_source_id` (Optional[str])
    - `index` (Optional[int])
    - `start_position_ticks` (Optional[int])
    - `format` (Optional[str])
    - `end_position_ticks` (Optional[int])
    - `copy_timestamps` (Optional[bool])
    - `add_vtt_time_map` (Optional[bool])
- `get_subtitle_tool`: Gets subtitles in a specified format.
  - **Parameters**:
    - `route_item_id` (str)
    - `route_media_source_id` (str)
    - `route_index` (int)
    - `route_format` (str)
    - `item_id` (Optional[str])
    - `media_source_id` (Optional[str])
    - `index` (Optional[int])
    - `format` (Optional[str])
    - `end_position_ticks` (Optional[int])
    - `copy_timestamps` (Optional[bool])
    - `add_vtt_time_map` (Optional[bool])
    - `start_position_ticks` (Optional[int])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-suggestions

**Description:** "Generated skill for Suggestions operations. Contains 1 tools."

#### Overview
This skill handles operations related to Suggestions.

#### Available Tools
- `get_suggestions_tool`: Gets suggestions.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `media_type` (Optional[List[Any]])
    - `type` (Optional[List[Any]])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `enable_total_record_count` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-sync-play

**Description:** "Generated skill for SyncPlay operations. Contains 22 tools."

#### Overview
This skill handles operations related to SyncPlay.

#### Available Tools
- `sync_play_get_group_tool`: Gets a SyncPlay group by id.
  - **Parameters**:
    - `id` (str)
- `sync_play_buffering_tool`: Notify SyncPlay group that member is buffering.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_join_group_tool`: Join an existing SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_leave_group_tool`: Leave the joined SyncPlay group.
- `sync_play_get_groups_tool`: Gets all SyncPlay groups.
- `sync_play_move_playlist_item_tool`: Request to move an item in the playlist in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_create_group_tool`: Create a new SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_next_item_tool`: Request next item in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_pause_tool`: Request pause in SyncPlay group.
- `sync_play_ping_tool`: Update session ping.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_previous_item_tool`: Request previous item in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_queue_tool`: Request to queue items to the playlist of a SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_ready_tool`: Notify SyncPlay group that member is ready for playback.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_remove_from_playlist_tool`: Request to remove items from the playlist in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_seek_tool`: Request seek in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_set_ignore_wait_tool`: Request SyncPlay group to ignore member during group-wait.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_set_new_queue_tool`: Request to set new playlist in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_set_playlist_item_tool`: Request to change playlist item in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_set_repeat_mode_tool`: Request to set repeat mode in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_set_shuffle_mode_tool`: Request to set shuffle mode in SyncPlay group.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `sync_play_stop_tool`: Request stop in SyncPlay group.
- `sync_play_unpause_tool`: Request unpause in SyncPlay group.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-system

**Description:** "Generated skill for System operations. Contains 10 tools."

#### Overview
This skill handles operations related to System.

#### Available Tools
- `get_endpoint_info_tool`: Gets information about the request endpoint.
- `get_system_info_tool`: Gets information about the server.
- `get_public_system_info_tool`: Gets public information about the server.
- `get_system_storage_tool`: Gets information about the server.
- `get_server_logs_tool`: Gets a list of available server log files.
- `get_log_file_tool`: Gets a log file.
  - **Parameters**:
    - `name` (Optional[str])
- `get_ping_system_tool`: Pings the system.
- `post_ping_system_tool`: Pings the system.
- `restart_application_tool`: Restarts the application.
- `shutdown_application_tool`: Shuts down the application.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-time-sync

**Description:** "Generated skill for TimeSync operations. Contains 1 tools."

#### Overview
This skill handles operations related to TimeSync.

#### Available Tools
- `get_utc_time_tool`: Gets the current UTC time.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-tmdb

**Description:** "Generated skill for Tmdb operations. Contains 1 tools."

#### Overview
This skill handles operations related to Tmdb.

#### Available Tools
- `tmdb_client_configuration_tool`: Gets the TMDb image configuration options.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-trailers

**Description:** "Generated skill for Trailers operations. Contains 1 tools."

#### Overview
This skill handles operations related to Trailers.

#### Available Tools
- `get_trailers_tool`: Finds movies and trailers similar to a given trailer.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `max_official_rating` (Optional[str])
    - `has_theme_song` (Optional[bool])
    - `has_theme_video` (Optional[bool])
    - `has_subtitles` (Optional[bool])
    - `has_special_feature` (Optional[bool])
    - `has_trailer` (Optional[bool])
    - `adjacent_to` (Optional[str])
    - `parent_index_number` (Optional[int])
    - `has_parental_rating` (Optional[bool])
    - `is_hd` (Optional[bool])
    - `is4_k` (Optional[bool])
    - `location_types` (Optional[List[Any]])
    - `exclude_location_types` (Optional[List[Any]])
    - `is_missing` (Optional[bool])
    - `is_unaired` (Optional[bool])
    - `min_community_rating` (Optional[float])
    - `min_critic_rating` (Optional[float])
    - `min_premiere_date` (Optional[str])
    - `min_date_last_saved` (Optional[str])
    - `min_date_last_saved_for_user` (Optional[str])
    - `max_premiere_date` (Optional[str])
    - `has_overview` (Optional[bool])
    - `has_imdb_id` (Optional[bool])
    - `has_tmdb_id` (Optional[bool])
    - `has_tvdb_id` (Optional[bool])
    - `is_movie` (Optional[bool])
    - `is_series` (Optional[bool])
    - `is_news` (Optional[bool])
    - `is_kids` (Optional[bool])
    - `is_sports` (Optional[bool])
    - `exclude_item_ids` (Optional[List[Any]])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `recursive` (Optional[bool])
    - `search_term` (Optional[str])
    - `sort_order` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `filters` (Optional[List[Any]])
    - `is_favorite` (Optional[bool])
    - `media_types` (Optional[List[Any]])
    - `image_types` (Optional[List[Any]])
    - `sort_by` (Optional[List[Any]])
    - `is_played` (Optional[bool])
    - `genres` (Optional[List[Any]])
    - `official_ratings` (Optional[List[Any]])
    - `tags` (Optional[List[Any]])
    - `years` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `person` (Optional[str])
    - `person_ids` (Optional[List[Any]])
    - `person_types` (Optional[List[Any]])
    - `studios` (Optional[List[Any]])
    - `artists` (Optional[List[Any]])
    - `exclude_artist_ids` (Optional[List[Any]])
    - `artist_ids` (Optional[List[Any]])
    - `album_artist_ids` (Optional[List[Any]])
    - `contributing_artist_ids` (Optional[List[Any]])
    - `albums` (Optional[List[Any]])
    - `album_ids` (Optional[List[Any]])
    - `ids` (Optional[List[Any]])
    - `video_types` (Optional[List[Any]])
    - `min_official_rating` (Optional[str])
    - `is_locked` (Optional[bool])
    - `is_place_holder` (Optional[bool])
    - `has_official_rating` (Optional[bool])
    - `collapse_box_set_items` (Optional[bool])
    - `min_width` (Optional[int])
    - `min_height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `is3_d` (Optional[bool])
    - `series_status` (Optional[List[Any]])
    - `name_starts_with_or_greater` (Optional[str])
    - `name_starts_with` (Optional[str])
    - `name_less_than` (Optional[str])
    - `studio_ids` (Optional[List[Any]])
    - `genre_ids` (Optional[List[Any]])
    - `enable_total_record_count` (Optional[bool])
    - `enable_images` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-trickplay

**Description:** "Generated skill for Trickplay operations. Contains 2 tools."

#### Overview
This skill handles operations related to Trickplay.

#### Available Tools
- `get_trickplay_tile_image_tool`: Gets a trickplay tile image.
  - **Parameters**:
    - `item_id` (str)
    - `width` (int)
    - `index` (int)
    - `media_source_id` (Optional[str])
- `get_trickplay_hls_playlist_tool`: Gets an image tiles playlist for trickplay.
  - **Parameters**:
    - `item_id` (str)
    - `width` (int)
    - `media_source_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-tv-shows

**Description:** "Generated skill for TvShows operations. Contains 4 tools."

#### Overview
This skill handles operations related to TvShows.

#### Available Tools
- `get_episodes_tool`: Gets episodes for a tv season.
  - **Parameters**:
    - `series_id` (str)
    - `user_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `season` (Optional[int])
    - `season_id` (Optional[str])
    - `is_missing` (Optional[bool])
    - `adjacent_to` (Optional[str])
    - `start_item_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `sort_by` (Optional[str])
- `get_seasons_tool`: Gets seasons for a tv series.
  - **Parameters**:
    - `series_id` (str)
    - `user_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `is_special_season` (Optional[bool])
    - `is_missing` (Optional[bool])
    - `adjacent_to` (Optional[str])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
- `get_next_up_tool`: Gets a list of next up episodes.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `series_id` (Optional[str])
    - `parent_id` (Optional[str])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `next_up_date_cutoff` (Optional[str])
    - `enable_total_record_count` (Optional[bool])
    - `disable_first_episode` (Optional[bool])
    - `enable_resumable` (Optional[bool])
    - `enable_rewatching` (Optional[bool])
- `get_upcoming_episodes_tool`: Gets a list of upcoming episodes.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `fields` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-universal-audio

**Description:** "Generated skill for UniversalAudio operations. Contains 1 tools."

#### Overview
This skill handles operations related to UniversalAudio.

#### Available Tools
- `get_universal_audio_stream_tool`: Gets an audio stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (Optional[List[Any]])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `user_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `max_audio_channels` (Optional[int])
    - `transcoding_audio_channels` (Optional[int])
    - `max_streaming_bitrate` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `start_time_ticks` (Optional[int])
    - `transcoding_container` (Optional[str])
    - `transcoding_protocol` (Optional[str])
    - `max_audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `enable_remote_media` (Optional[bool])
    - `enable_audio_vbr_encoding` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `enable_redirection` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-user-library

**Description:** "Generated skill for UserLibrary operations. Contains 10 tools."

#### Overview
This skill handles operations related to UserLibrary.

#### Available Tools
- `get_item_tool`: Gets an item from a user's library.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_intros_tool`: Gets intros to play before the main media item plays.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_local_trailers_tool`: Gets local trailers for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_special_features_tool`: Gets special features for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `get_latest_media_tool`: Gets latest media.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `is_played` (Optional[bool])
    - `enable_images` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `limit` (Optional[int])
    - `group_items` (Optional[bool])
- `get_root_folder_tool`: Gets the root folder from a user's library.
  - **Parameters**:
    - `user_id` (Optional[str])
- `mark_favorite_item_tool`: Marks an item as a favorite.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `unmark_favorite_item_tool`: Unmarks item as a favorite.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `delete_user_item_rating_tool`: Deletes a user's saved personal rating for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `update_user_item_rating_tool`: Updates a user's rating for an item.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
    - `likes` (Optional[bool])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-user-views

**Description:** "Generated skill for UserViews operations. Contains 2 tools."

#### Overview
This skill handles operations related to UserViews.

#### Available Tools
- `get_user_views_tool`: Get user views.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `include_external_content` (Optional[bool])
    - `preset_views` (Optional[List[Any]])
    - `include_hidden` (Optional[bool])
- `get_grouping_options_tool`: Get user view grouping options.
  - **Parameters**:
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-user

**Description:** "Generated skill for User operations. Contains 14 tools."

#### Overview
This skill handles operations related to User.

#### Available Tools
- `get_users_tool`: Gets a list of users.
  - **Parameters**:
    - `is_hidden` (Optional[bool])
    - `is_disabled` (Optional[bool])
- `update_user_tool`: Updates a user.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `get_user_by_id_tool`: Gets a user by Id.
  - **Parameters**:
    - `user_id` (str)
- `delete_user_tool`: Deletes a user.
  - **Parameters**:
    - `user_id` (str)
- `update_user_policy_tool`: Updates a user policy.
  - **Parameters**:
    - `user_id` (str)
    - `body` (Optional[Dict[str, Any]])
- `authenticate_user_by_name_tool`: Authenticates a user by name.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `authenticate_with_quick_connect_tool`: Authenticates a user with quick connect.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `update_user_configuration_tool`: Updates a user configuration.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `forgot_password_tool`: Initiates the forgot password process for a local user.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `forgot_password_pin_tool`: Redeems a forgot password pin.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `get_current_user_tool`: Gets the user based on auth token.
- `create_user_by_name_tool`: Creates a user.
  - **Parameters**:
    - `body` (Optional[Dict[str, Any]])
- `update_user_password_tool`: Updates a user's password.
  - **Parameters**:
    - `user_id` (Optional[str])
    - `body` (Optional[Dict[str, Any]])
- `get_public_users_tool`: Gets a list of publicly visible users for display on a login screen.

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-video-attachments

**Description:** "Generated skill for VideoAttachments operations. Contains 1 tools."

#### Overview
This skill handles operations related to VideoAttachments.

#### Available Tools
- `get_attachment_tool`: Get video attachment.
  - **Parameters**:
    - `video_id` (str)
    - `media_source_id` (str)
    - `index` (int)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-videos

**Description:** "Generated skill for Videos operations. Contains 5 tools."

#### Overview
This skill handles operations related to Videos.

#### Available Tools
- `get_additional_part_tool`: Gets additional parts for a video.
  - **Parameters**:
    - `item_id` (str)
    - `user_id` (Optional[str])
- `delete_alternate_sources_tool`: Removes alternate video sources.
  - **Parameters**:
    - `item_id` (str)
- `get_video_stream_tool`: Gets a video stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (Optional[str])
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `get_video_stream_by_container_tool`: Gets a video stream.
  - **Parameters**:
    - `item_id` (str)
    - `container` (str)
    - `static` (Optional[bool])
    - `params` (Optional[str])
    - `tag` (Optional[str])
    - `device_profile_id` (Optional[str])
    - `play_session_id` (Optional[str])
    - `segment_container` (Optional[str])
    - `segment_length` (Optional[int])
    - `min_segments` (Optional[int])
    - `media_source_id` (Optional[str])
    - `device_id` (Optional[str])
    - `audio_codec` (Optional[str])
    - `enable_auto_stream_copy` (Optional[bool])
    - `allow_video_stream_copy` (Optional[bool])
    - `allow_audio_stream_copy` (Optional[bool])
    - `break_on_non_key_frames` (Optional[bool])
    - `audio_sample_rate` (Optional[int])
    - `max_audio_bit_depth` (Optional[int])
    - `audio_bit_rate` (Optional[int])
    - `audio_channels` (Optional[int])
    - `max_audio_channels` (Optional[int])
    - `profile` (Optional[str])
    - `level` (Optional[str])
    - `framerate` (Optional[float])
    - `max_framerate` (Optional[float])
    - `copy_timestamps` (Optional[bool])
    - `start_time_ticks` (Optional[int])
    - `width` (Optional[int])
    - `height` (Optional[int])
    - `max_width` (Optional[int])
    - `max_height` (Optional[int])
    - `video_bit_rate` (Optional[int])
    - `subtitle_stream_index` (Optional[int])
    - `subtitle_method` (Optional[str])
    - `max_ref_frames` (Optional[int])
    - `max_video_bit_depth` (Optional[int])
    - `require_avc` (Optional[bool])
    - `de_interlace` (Optional[bool])
    - `require_non_anamorphic` (Optional[bool])
    - `transcoding_max_audio_channels` (Optional[int])
    - `cpu_core_limit` (Optional[int])
    - `live_stream_id` (Optional[str])
    - `enable_mpegts_m2_ts_mode` (Optional[bool])
    - `video_codec` (Optional[str])
    - `subtitle_codec` (Optional[str])
    - `transcode_reasons` (Optional[str])
    - `audio_stream_index` (Optional[int])
    - `video_stream_index` (Optional[int])
    - `context` (Optional[str])
    - `stream_options` (Optional[Dict[str, Any]])
    - `enable_audio_vbr_encoding` (Optional[bool])
- `merge_versions_tool`: Merges videos into a single record.
  - **Parameters**:
    - `ids` (Optional[List[Any]])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### jellyfin-years

**Description:** "Generated skill for Years operations. Contains 2 tools."

#### Overview
This skill handles operations related to Years.

#### Available Tools
- `get_years_tool`: Get years.
  - **Parameters**:
    - `start_index` (Optional[int])
    - `limit` (Optional[int])
    - `sort_order` (Optional[List[Any]])
    - `parent_id` (Optional[str])
    - `fields` (Optional[List[Any]])
    - `exclude_item_types` (Optional[List[Any]])
    - `include_item_types` (Optional[List[Any]])
    - `media_types` (Optional[List[Any]])
    - `sort_by` (Optional[List[Any]])
    - `enable_user_data` (Optional[bool])
    - `image_type_limit` (Optional[int])
    - `enable_image_types` (Optional[List[Any]])
    - `user_id` (Optional[str])
    - `recursive` (Optional[bool])
    - `enable_images` (Optional[bool])
- `get_year_tool`: Gets a year.
  - **Parameters**:
    - `year` (int)
    - `user_id` (Optional[str])

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.
