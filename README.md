# IPTV Media Source for Home Assistant


This custom integration for Home Assistant allows you to add M3U IPTV playlists as a media source. You can either select from a list of countries provided by the [iptv-org/api](https://github.com/iptv-org/api) project or provide your own custom M3U/M3U8 URL.

Once configured, you can browse and play individual channels from your IPTV playlists directly within Home Assistant's media browser.

## Features

* **IPTV.org Integration**: Easily add country-specific M3U playlists from the extensive [iptv-org](https://github.com/iptv-org) collection.
* **Custom M3U/M3U8 Support**: Add any publicly accessible M3U or M3U8 playlist URL.
* **Channel Browsing**: Navigate through individual channels within your configured playlists directly from the Home Assistant Media Browser.
* **Channel Playback**: Play selected IPTV channels on compatible media player entities in Home Assistant.
* **Channel Logos**: Displays channel logos (`tvg-logo` from M3U) in the media browser where available.
* **Caching**: M3U playlist content is cached to improve performance and reduce load on source servers.

## Installation

You can install this integration via HACS (recommended) or manually.

### Option 1: HACS (Home Assistant Community Store)

1.  **Ensure HACS is installed.** If not, follow the [HACS installation guide](https://hacs.xyz/docs/setup/download).
2.  **Add as a Custom Repository:**
    * Open HACS in Home Assistant (usually in the sidebar).
    * Go to "Integrations".
    * Click the three dots in the top right corner and select "Custom repositories".
    * In the "Repository" field, paste the URL of **your GitHub repository** for this integration (e.g., `https://github.com/yohaybn/iptv_media_source`).
    * In the "Category" field, select "Integration".
    * Click "Add".
3.  **Install the Integration:**
    * Search for "IPTV Media Source" in HACS Integrations.
    * Click "Install".
    * Follow the on-screen prompts.
 4. **Restart Home Assistant:** * Go to Developer Tools -> Server Management (or Settings -> System -> Restart button in newer HA versions). * Click "Restart".
### Option 2: Manual Installation
 <details>
	<summary>Manual Installation</summary>
	
1.  **Download the Integration Files:**
    * Download the latest release `zip` file from **your GitHub repository's releases page**.
    * Alternatively, clone or download the repository source code.
2.  **Copy Files to `custom_components`:**
    * Inside your Home Assistant configuration directory, create a folder named `custom_components` if it doesn't already exist.
    * Inside `custom_components`, create a folder named `iptv_media_source`.
    * Copy all the files and folders from the downloaded/cloned integration's `custom_components/iptv_media_source/` directory into the `config/custom_components/iptv_media_source/` directory you just created.
    Your final directory structure should look like this:
    ```
    <config_directory>/
    └── custom_components/
        └── iptv_media_source/
            ├── __init__.py
            ├── manifest.json
            ├── config_flow.py
            ├── media_source.py
            ├── const.py
            ├── strings.json
            └── translations/
                └── en.json
    ```
3.  **Restart Home Assistant:**
    * Go to Developer Tools -> Server Management (or Settings -> System -> Restart button in newer HA versions).
    * Click "Restart".
</details>

## Configuration

After installation and restarting Home Assistant, you can add IPTV Media Sources:

1.  Go to **Settings** -> **Devices & Services**.
2.  Click the **+ ADD INTEGRATION** button in the bottom right corner.
3.  Search for "**IPTV Media Source**" and select it.
4.  The configuration flow will start:
    * **Source Type**:
        * **Select from IPTV.org list**: Allows you to choose a country. The integration will use the general M3U playlist for that country from IPTV.org. 
        * **Provide custom M3U8 URL**: Allows you to enter your own M3U/M3U8 playlist URL and a friendly name.
    * Follow the prompts based on your selection.
5.  Once added, the IPTV source will be available in the Home Assistant Media Browser (usually found in the sidebar under "Media" or by selecting a media player entity that supports browsing).

You can add multiple instances of this integration to include various IPTV.org countries or custom M3U playlists.

## Usage

1.  Open the **Media Browser** in Home Assistant.
2.  Look for the "IPTV Media" section (or the friendly name you provided if you configured multiple sources).
3.  Click on a configured IPTV source (e.g., "IPTV.org - United States" or "My Custom Playlist").
4.  The integration will fetch and display the channels from that M3U playlist.
5.  Click on a channel to start playback on a compatible media player.

## Options

For configured IPTV Media Sources, you can adjust some options:

1.  Go to **Settings** -> **Devices & Services**.
2.  Find your "IPTV Media Source" entry and click on it.
3.  Click "CONFIGURE" (or the options/pencil icon).
    * You can typically change the "Friendly Name".
    * For "Custom URL" types, you can also change the M3U URL.
    * For "IPTV.org" types, the M3U URL is tied to the country and cannot be changed via options (you would need to remove and re-add the source to change the country).

## Troubleshooting

* **"Could not fetch country list" / "No countries found" (IPTV.org)**:
    * Ensure your Home Assistant instance has a working internet connection.
    * The IPTV.org API might be temporarily unavailable. Try again later or use a custom URL.
* **Channels not loading / Playback issues**:
    * Verify the M3U URL is correct and publicly accessible. Open it in a browser or VLC player to test.
    * Some channels in public M3U lists may be geo-restricted or offline. This integration cannot control the availability or quality of streams within the M3U files.
    * Check Home Assistant logs (Settings -> System -> Logs) for any errors related to `iptv_media_source` or media playback.


## Contributing

Contributions are welcome! If you have ideas for improvements or find bugs, please open an issue or submit a pull request.


