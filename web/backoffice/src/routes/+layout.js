import {getConfigurationFromFile} from "$sharedLib/utils";
import {fileConfiguration} from "$sharedLib/stores";
import { browser } from "$app/environment";

// Load configuration from file before
// any other component code runs
async function loadConfig() {
    let config = await getConfigurationFromFile() ?? {};
    config.backend_present = true;
    fileConfiguration.set(config);
}

if (browser) {
    loadConfig()
        .catch(error => console.log('Error while trying to load config from file:', error));
}
