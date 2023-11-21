import {get} from "svelte/store";
import {NostrGlobalConfig, Info} from "$sharedLib/stores";
import {getDomainName} from "$sharedLib/utils";
import {publishConfiguration} from "$sharedLib/services/nostr";

- PENSAR SI QUITAR PARAMS Y PONERLO TODO EN LA RAIZ DE LA SECCIÓN
    ** RAZÓN PARA DEJAR PARAMS = DISTINTOS WIDGETS TIENEN DISTINTOS PARÁMETROS

- DONDE Y COMO GUARDAR LOS IDS DE LAS COSAS ELEGIDAS. EN LA PROPIA SECCIÓN, EN UN .DATA ??

removeStallFromHomePage
addStallToHomePage

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

export function getPageContent(page, globalConfig = get(NostrGlobalConfig)) {
    const domainName = getDomainName();

    if (
        !globalConfig.content ||
        !globalConfig.content.hasOwnProperty(domainName) ||
        !globalConfig.content[domainName].pages ||
        !globalConfig.content[domainName].pages.hasOwnProperty(page) ||
        !globalConfig.content[domainName].pages[page].sections
    ) {
        return null;
    }

    return globalConfig.content[domainName].pages[page];
}

export function getSection() {

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
    let pageContent = getPageContent(pageId);

    let section = pageContent.sections[sectionId];

    section.title = setupParams.sectionTitle;

    if (section.params === undefined) {
        section.params = {};
    }

    section.params.sectionType = setupParams.sectionType;
    section.params.maxProductsShown = setupParams.maxProductsShown;

    NostrGlobalConfigFireReactivity();
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
export function addItem(newSection, pageId = 0) {
    let pageContent = getPageContent(pageId);

    if (newSection !== '') {
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
            title: newSection,
            order: order
        };

        NostrGlobalConfigFireReactivity();

        saveContentToNostr();

        return sectionIdNewElement;
    }

    return null;
}

export const handleEnd = (pageId, evt) => {
    let pageContent = getPageContent(pageId);
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

export function removeItem(pageId, index) {
    let pageContent = getPageContent(pageId);

    pageContent.sections = Object.keys(pageContent.sections)
        .filter(section => {console.log('---section:',section); console.log('---index:',index); console.log('---section == index:',section == index); return section !== index})
        .reduce((obj, key) => {
            obj[key] = pageContent.sections[key];
            return obj;
        }, {});

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

function setSectionsOrder(pageId) {
    let pageContent = getPageContent(pageId);

    let order = 0;
    pageContent.sections.forEach(section => {
        section.order = order;
        order++;
    });

    setPageContent(pageId, pageContent);
}

export function saveContentToNostr() {
    return;

    const pages = getPages();

    pages.forEach(page => {
        setSectionsOrder(page);
    });

    console.log(' *** saveContentToNostr ----------- NOT REALLY SAVING TO NOSTR ----------- ****');
    /*
    publishConfiguration(globalConfig,
        () => {
            console.log('Configuration saved to Nostr relay!!');
        });
    */
    Info.set("Configuration saved to Nostr.");
}
