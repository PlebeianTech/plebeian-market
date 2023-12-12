import {getConfigurationFromFile} from "$sharedLib/utils";
import {fileConfiguration} from "$sharedLib/stores";

export const prerender = true;

// Load configuration from file before
// any other component code runs
async function loadConfig() {
    let config = await getConfigurationFromFile() ?? {};
    if (!Object.prototype.hasOwnProperty.call(config, 'backend_present')) {
        config.backend_present = true;
    }
    fileConfiguration.set(config);
}

loadConfig()
    .catch(error => console.log('Error while trying to load config from file:', error));
