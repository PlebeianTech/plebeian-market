import {get} from "svelte/store";
import {NostrGlobalConfig, Info} from "$sharedLib/stores";
import {publishConfiguration, getConfigurationKey} from "$sharedLib/services/nostr";

export const pageBuilderWidgetType = {
    text: {
        'title': 'Show a long Text',
        'description': 'This widget allows you to write a text to explain something to your customers (about me, about this site, ...).',
        'items': false,
        'max_num_available': false,
        'markdownText': true
    },
    products: {
        'title': 'Show selected Products',
        'description': 'This widget allows you to be able to select which products you want shown on this section.',
        'items': ['products'],
        'max_num_available': false
    },
    products_with_slider: {
        'title': 'Show selected Products in a Slider with text',
        'description': "This widget allows you to select which products you want shown on a big slider with a description. The slider will show the product's title and description by default, but you can change that to other text of your choice.",
        'items': ['products'],
        'max_num_available': false,
        'markdownText': true
    },
    stalls: {
        'title': 'Show selected Stalls',
        'description': 'This widget allows you to be able to select which stalls you want shown on this section.',
        'items': ['stalls'],
        'max_num_available': false
    },
    /*
    stall_products: {
        'title': 'Show all Products from several stalls',
        'description': 'This widget allows you to select one or several stalls to have all their products automatically shown in the section.',
        'items': ['stalls'],
        'max_num_available': true
    },
    */
    /*
    banner: {
        'title': 'Banner',
        'description': 'This widget allows you to show an image occupying the whole width of the screen.',
        'items': [],
        'max_num_available': false,
        'image_selector': true
    },
    */
};

export function getPages(globalConfig = get(NostrGlobalConfig)): object {
    if (
        !globalConfig.content ||
        !globalConfig.content.pages
    ) {
        return {};
    }

    return globalConfig.content.pages;
}

export function getPage(pageId, globalConfig = get(NostrGlobalConfig)) {
    if (
        !globalConfig?.content ||
        !globalConfig?.content.pages ||
        !globalConfig?.content.pages.hasOwnProperty(pageId) ||
        !globalConfig?.content.pages[pageId].sections
    ) {
        return null;
    }

    return globalConfig.content.pages[pageId];
}

export function getSection(pageId, sectionId) {
    return getPage(pageId)?.sections[sectionId] ?? null;
}

function setPageContent(pageId, content, globalConfig = get(NostrGlobalConfig)) {
    if (!content) {
        return null;
    }

    globalConfig.content.pages[pageId] = content;

    NostrGlobalConfig.set(globalConfig);
}

export function saveSectionSetup(pageId, sectionId, setupParams) {
    let section = getSection(pageId, sectionId);

    section.title = setupParams.sectionTitle;

    if (section.params === undefined) {
        section.params = {};
    }

    section.params.sectionType = setupParams.sectionType;

    if (setupParams.maxProductsShown && setupParams.maxProductsShown != 0) {
        section.params.maxProductsShown = setupParams.maxProductsShown;
    }

    if (setupParams.markDownContent) {
        let configurationKey;

        if (setupParams.sectionType === 'text') {
            configurationKey = 'sectionText_' + pageId + '_' + sectionId;
        } else if (setupParams.sectionType === 'products_with_slider') {
            configurationKey = 'section_products_with_slider_' + pageId + '_' + sectionId + '_' + setupParams.lastProductPassed.id
        }

        publishConfiguration(setupParams.markDownContent, getConfigurationKey(configurationKey),
            () => {
                console.log('markDownContent saved to Nostr relay!!');
            });
    }

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

function NostrGlobalConfigFireReactivity() {
    NostrGlobalConfig.set(get(NostrGlobalConfig));
}

// pageId == 0 is always the homepage
export function addSectionToPage(newSectionName: string, pageId = 0) {
    if (newSectionName !== '') {
        // Initializes the 'content' structure the first time the user wants to add a section to homepage
        if (pageId == 0 && getPage(0) === null) {
            let globalConfig = get(NostrGlobalConfig);

            globalConfig.content = {
                pages: {
                    0: {
                        title: 'Homepage',
                        sections: {
                            0: {
                                title: newSectionName ?? 'Main',
                                order: 0
                            }
                        }
                    }
                }
             };

            NostrGlobalConfig.set(globalConfig);

            saveContentToNostr();

            return 0;

        } else {
            let pageContent = getPage(pageId);

            let sectionIdNewElement = 0;
            let order = 0;

            Object.keys(pageContent.sections).forEach(section_id => {
                if (section_id > sectionIdNewElement) {
                    sectionIdNewElement = section_id;
                }
                if (pageContent.sections[section_id].order > order) {
                    order = pageContent.sections[section_id].order;
                }
            });

            sectionIdNewElement++;
            order++;

            pageContent.sections[sectionIdNewElement] = {
                title: newSectionName,
                order: order
            };

            NostrGlobalConfigFireReactivity();

            saveContentToNostr();

            return sectionIdNewElement;
        }
    }

    return null;
}

export const handleMove = (pageId, evt) => {
    let pageContent = getPage(pageId);

    let orderedSections = Object.entries(pageContent.sections).sort((a, b) => {
        return a[1].order - b[1].order;
    });

    let initialArrayOfOrderedSectionIDs: string[] = [];
    orderedSections.forEach(sectionId => {
        initialArrayOfOrderedSectionIDs.push(sectionId[0])
    });

    // move elements in the initial array as the movement made by the user
    const elm = initialArrayOfOrderedSectionIDs.splice(evt.oldIndex, 1)[0];
    initialArrayOfOrderedSectionIDs.splice(evt.newIndex, 0, elm);

    let newPageContentSections = {};
    let order = 0;

    initialArrayOfOrderedSectionIDs.forEach(sectionId => {
        newPageContentSections[sectionId] = pageContent.sections[sectionId];
        newPageContentSections[sectionId].order = order;
        order++;
    });

    pageContent.sections = newPageContentSections;

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

export function removeSection(pageId, sectionId) {
    let pageContent = getPage(pageId);

    pageContent.sections = Object.keys(pageContent.sections)
        .filter(section => {return section !== sectionId})
        .reduce((obj, key) => {
            obj[key] = pageContent.sections[key];
            return obj;
        }, {});

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

export function saveContentToNostr() {
    let globalConfig = get(NostrGlobalConfig);
    delete globalConfig.homepage_include_stalls;

    //console.log('Saving this to Nostr:', globalConfig);

    publishConfiguration(globalConfig, getConfigurationKey('site_specific_config'),
        () => {
            console.log('Configuration saved to Nostr relay!!');
        });

    Info.set("Configuration saved to Nostr.");
}

/*****************************************
            ITEM MANAGEMENT
******************************************/
export function addItemToSection(pageId, sectionId, itemId, entityName) {
    let section = getSection(pageId, sectionId);

    if (!section.values) {
        section.values = {};
    }

    if (!section.values[entityName]) {
        section.values[entityName] = [];
    }

    if (!section.values[entityName].includes(itemId)) {
        section.values[entityName].push(itemId);

        NostrGlobalConfigFireReactivity();

        saveContentToNostr();
    }
}

export function removeItemFromSection(pageId, sectionId, itemId, entityName) {
    let section = getSection(pageId, sectionId);

    section.values[entityName] = section.values[entityName].filter(itemIdIterating => {
        return itemIdIterating !== itemId;
    });

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

export function getItemsFromSection(pageId, sectionId, entityName) {
    let section = getSection(pageId, sectionId);

    if (section && section.values && section.values.hasOwnProperty(entityName)) {
        return section.values[entityName] ?? [];
    }

    return [];
}

export function getPlacesWhereItemIsPresent(itemId, entityName) {
    let places: string[] = [];

    let pages = getPages();

    if (pages) {
        Object.keys(pages).forEach(pageId => {
            Object.keys(pages[pageId].sections).forEach(sectionId => {
                if (pages[pageId].sections[sectionId].values && pages[pageId].sections[sectionId].values[entityName]?.includes(itemId)) {
                    places[pageId + '-' + sectionId] = pages[pageId].title + ' / ' + pages[pageId].sections[sectionId].title
                }
            });
        });
    }

    return places;
}
