import {get} from "svelte/store";
import {NostrGlobalConfig, Info} from "$sharedLib/stores";
import {getDomainName} from "$sharedLib/utils";
import {publishConfiguration} from "$sharedLib/services/nostr";

export const pageBuilderWidgetType = {
    products: {
        'title': 'Selected products',
        'description': 'Choose this widget type to be able to select which products you want shown on this section.',
        'items': ['products'],
        'max_num_available': false
    },
    stalls: {
        'title': 'Selected stalls',
        'description': 'Choose this widget type to be able to select which stalls you want shown on this section.',
        'items': ['stalls'],
        'max_num_available': false
    },
    stall_products: {
        'title': 'All products from several stalls',
        'description': 'Choose this widget type to be able to select one or several stalls to have all their products automatically shown in the section.',
        'items': ['stalls'],
        'max_num_available': true
    },
    /*
    banner: {
        'title': 'Banner',
        'description': 'Choose this widget type to show an image occupying the whole width of the screen.',
        'items': [],
        'max_num_available': false,
        'image_selector': true
    },
    */
};

export function getPages(globalConfig = get(NostrGlobalConfig)) {
    const domainName = getDomainName();

    if (
        !globalConfig.content ||
        !globalConfig.content.hasOwnProperty(domainName) ||
        !globalConfig.content[domainName].pages
    ) {
        return null;
    }

    return globalConfig.content[domainName].pages;
}

export function getPage(pageId, globalConfig = get(NostrGlobalConfig)) {
    const domainName = getDomainName();

    if (
        !globalConfig.content ||
        !globalConfig.content.hasOwnProperty(domainName) ||
        !globalConfig.content[domainName].pages ||
        !globalConfig.content[domainName].pages.hasOwnProperty(pageId) ||
        !globalConfig.content[domainName].pages[pageId].sections
    ) {
        return null;
    }

    return globalConfig.content[domainName].pages[pageId];
}

export function getSection(pageId, sectionId) {
    return getPage(pageId)?.sections[sectionId] ?? null;
}

function setPageContent(pageId, content, globalConfig = get(NostrGlobalConfig)) {
    const domainName = getDomainName();

    if (!content) {
        return null;
    }

    globalConfig.content[domainName].pages[pageId] = content;
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

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

function NostrGlobalConfigFireReactivity() {
    NostrGlobalConfig.set(get(NostrGlobalConfig));
}

export function initializeContentForGlobalConfig(globalConfig = get(NostrGlobalConfig)) {
    const domainName = getDomainName();

    if (!globalConfig.content) {
        globalConfig.content = {
            [domainName]: {
                pages: {
                    0: {
                        title: 'Homepage',
                        sections: {
                            0: {
                                title: 'Main',
                                order: 0
                            }
                        }
                    }
                }
            }
        };
        NostrGlobalConfig.set(globalConfig);

        console.log('   --- se CREA - globalConfig:', globalConfig);

        saveContentToNostr();
    }
}

// page_id == 0 is always the homepage
export function addSectionToPage(newSectionName: string, pageId = 0) {
    let pageContent = getPage(pageId);

    if (newSectionName !== '') {
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

    return null;
}

export const handleEnd = (pageId, evt) => {
    let pageContent = getPage(pageId);
console.log('INICIO pageContent=', pageContent);

    let sectionKeysArray = Object.keys(pageContent.sections);
    console.log('sectionKeysArray',sectionKeysArray);

    // move
    const elm = sectionKeysArray.splice(evt.oldIndex, 1)[0];
    sectionKeysArray.splice(evt.newIndex, 0, elm);

    console.log('sectionKeysArray_222',sectionKeysArray);
/*
    pageContent.sections = sectionKeysArray.reduce((obj, key) => {
        obj[key] = pageContent.sections[key];
        return obj;
    }, {});
*/

    let order = 0;
    pageContent.sections = sectionKeysArray.reduce((obj, key) => {
        console.log('key', key);
        obj[key] = {
            order: order,
            title: pageContent.sections[key].title
        }
        order++;
        return obj;
    }, {});

    setPageContent(pageId, pageContent);
    console.log('pageContent.sections____22222', pageContent.sections);

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

// TODO: maybe this is not needed anymore if we always keep the sections ordered
/*
function setSectionsOrder(pageId) {
    let pageContent = getPage(pageId);

    let order = 0;
    pageContent.sections.forEach(section => {
        section.order = order;
        order++;
    });

    setPageContent(pageId, pageContent);
}
*/

export function saveContentToNostr() {
    /*
    const pages = getPages();

    pages.forEach(page => {
        setSectionsOrder(page);
    });
    */

    console.log(' *** saveContentToNostr ----------- NOT REALLY SAVING TO NOSTR ----------- ****');

    let globalConfig = get(NostrGlobalConfig);
    delete globalConfig.homepage_include_stalls;

    console.log('Saving this to Nostr:', globalConfig);
/*
    publishConfiguration(globalConfig,
        () => {
            console.log('Configuration saved to Nostr relay!!');
        });
 */
    Info.set("Configuration saved to Nostr.");
}

/*****************************************
            ITEM MANAGEMENT
******************************************/
export function addItemToSection(pageId, sectionId, itemId, entityName) {
    let section = getSection(pageId, sectionId)

    if (!section.values) {
        section.values = {};
    }

    if (!section.values[entityName]) {
        section.values[entityName] = []
    }

    if (!section.values[entityName].includes(itemId)) {
        section.values[entityName].push(itemId);

// TODO REACTIVITY
        section.values[entityName] = section.values[entityName];

        console.log('---- section_AFTER:', section);

        console.log('addItemToSection - Pushing changes to Nostr...');

// TODO REACTIVITY
        NostrGlobalConfigFireReactivity();

        saveContentToNostr()
    }
}

export function removeItemFromSection(pageId, sectionId, itemId, entityName) {
    let section = getSection(pageId, sectionId)

    section.values[entityName] = section.values[entityName].filter(itemIdIterating => {
        return itemIdIterating !== itemId;
    });

    console.log('removeItemFromSection - Pushing changes to Nostr...');

    NostrGlobalConfigFireReactivity();

    // saveContentToNostr()
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
