import {get} from "svelte/store";
import {NostrGlobalConfig, Info} from "$sharedLib/stores";
import {publishConfiguration, getConfigurationKey} from "$sharedLib/services/nostr";
import {Error} from "$sharedLib/stores";
import DOMPurify from "dompurify";

export const pageBuilderWidgetType = {
    text: {
        'title': 'Text Block',
        'description': 'This widget allows you to write a text to explain something to your customers (about me, about this site, ...).',
        'items': false,
        'max_num_available': false,
        'richText': true
    },
    products: {
        'title': 'Selected Products',
        'description': 'This widget allows you to be able to select which products you want shown on this section.',
        'items': ['products'],
        'max_num_available': false
    },
    products_with_slider: {
        'title': 'Selected Products in a Slider with text',
        'description': "This widget allows you to select which products you want shown on a big slider with a description. The slider will show the product's title and description by default, but you can change that to other text of your choice.",
        'items': ['products'],
        'max_num_available': false,
        'richText': true
    },
    stalls: {
        'title': 'Selected Stalls',
        'description': 'This widget allows you to be able to select which stalls you want shown on this section.',
        'items': ['stalls'],
        'max_num_available': false
    },
    image_banner: {
        'title': 'Image Banner',
        'description': 'This widget allows you to show an image banner in a section',
        'items': false,
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

export const pagesAndTitles = {
    about: {
        title: 'About'
    },
    marketsquare: {
        title: 'Market Square'
    },
    planet: {
        title: 'Planet Plebeian'
    },
    stalls: {
        title: 'Stall Explorer'
    },
    universe: {
        title: 'Nostr Universe'
    },
    cart: {
        title: 'Shopping Cart'
    },
    contact: {
        title: 'Contact'
    },
    donations: {
        title: 'Donations'
    },
    faq: {
        title: 'FAQ'
    },
    messages: {
        title: 'Messages'
    },
    orders: {
        title: 'Orders'
    },
    settings: {
        title: 'Settings'
    },
    skills: {
        title: 'Skills'
    },
    auctions: {
        title: 'Pending Auctions'
    }
};

export const pagesEnabledByDefault = ['stalls', 'marketsquare', 'planet', 'universe'];

/*****************************************
                   GET
 ******************************************/
export function getPages(globalConfig = get(NostrGlobalConfig)): object {
    if (globalConfig?.content?.pages) {
        return globalConfig.content.pages;
    }

    return {};
}

export function getPage(pageId, globalConfig = get(NostrGlobalConfig)) {
    if (globalConfig?.content?.pages?.hasOwnProperty(pageId)) {
        return globalConfig.content.pages[pageId];
    }

    return null;
}

export function getSection(pageId, sectionId) {
    return getPage(pageId)?.sections[sectionId] ?? null;
}

export function getPageIdForSlug(slug: string) {
    if (slug === '/') return 0;

    for (const [pageId, page] of Object.entries(getPages())) {
        if (slug === page.slug) {
            return pageId;
        }
    }

    return false;
}

/*****************************************
                   ADD
 ******************************************/
export function addPage(newPageName: string) {
    if (newPageName !== '') {
        let pages = getPages();

        let maxPageId = 0;

        for (const [pageId] of Object.entries(getPages())) {
            if (pageId > maxPageId) {
                maxPageId = pageId;
            }
        }

        maxPageId++;

        pages[maxPageId] = {
            title: newPageName
        };

        NostrGlobalConfigFireReactivity();

        saveContentToNostr();

        return maxPageId;
    }
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
                        slug: '/',
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

            let sectionIdNewElement: number = 0;
            let order: number = 0;

            if (pageContent.sections) {
                Object.keys(pageContent.sections).forEach(section_id => {
                    if (parseInt(section_id, 10) > sectionIdNewElement) {
                        sectionIdNewElement = parseInt(section_id, 10);
                    }
                    if (pageContent.sections[section_id].order > order) {
                        order = pageContent.sections[section_id].order;
                    }
                });

                sectionIdNewElement++;
                order++;
            } else {
                pageContent.sections = {};
            }

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


/*****************************************
                   SET
 ******************************************/
function setPageContent(pageId, content, globalConfig = get(NostrGlobalConfig)) {
    if (!content) {
        return null;
    }

    globalConfig.content.pages[pageId] = content;

    NostrGlobalConfig.set(globalConfig);
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

export function setLogo(logoURL: string) {
    let globalConfig = get(NostrGlobalConfig)
    globalConfig.content.logo = logoURL;
    NostrGlobalConfig.set(globalConfig);
    saveContentToNostr();
}
export function setFavicon(faviconURL: string) {
    let globalConfig = get(NostrGlobalConfig)
    globalConfig.content.favicon = faviconURL;
    NostrGlobalConfig.set(globalConfig);
    saveContentToNostr();
}
export function setWebsiteTitle(title: string) {
    let globalConfig = get(NostrGlobalConfig)
    globalConfig.content.title = title;
    NostrGlobalConfig.set(globalConfig);
    saveContentToNostr();
}

export function savePageParams(pageId, newPageTitle: string, newPageSlug: string) {
    if (!newPageTitle || !newPageSlug) {
        Error.set('A page needs to have a title and a slug.');
    }

    if (newPageSlug.startsWith('/')) {
        newPageSlug = newPageSlug.substring(1);
    }

    const appRoutes = getAppRoutes();
    if (appRoutes.includes(newPageSlug)) {
        Error.set('You cannot use a slug from the list of reserved pages: ' + appRoutes.join(', '));
        return;
    }

    const page = getPage(pageId);
    page.title = newPageTitle;
    page.slug = newPageSlug;

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

/*****************************************
                  REMOVE
 ******************************************/
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

export function removePage(pageId) {
    if (pageId == 0) {
        Error.set('Homepage cannot be deleted');
        return;
    }

    let pages = getPages();

    delete pages[pageId];

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
}

/*****************************************
            SAVE and REACTIVITY
 ******************************************/
function NostrGlobalConfigFireReactivity() {
    NostrGlobalConfig.set(get(NostrGlobalConfig));
}
export function saveContentToNostr() {
    let globalConfig = get(NostrGlobalConfig);
    delete globalConfig.homepage_include_stalls;

    publishConfiguration(globalConfig, getConfigurationKey('site_specific_config'),
        () => {
            console.log('Configuration saved to Nostr relay!!');
        });

    Info.set("Configuration saved to Nostr.");
}

export function saveSectionSetup(pageId, sectionId, setupParams) {
    let section = getSection(pageId, sectionId);

    section.title = setupParams.sectionTitle;

    if (section.params === undefined) {
        section.params = {};
    }

    section.params.sectionType = setupParams.sectionType;

    if (setupParams.sectionType === 'image_banner') {
        section.params.imageBannerURL = setupParams.imageBannerURL ?? '';
    }

    if (setupParams.maxProductsShown && setupParams.maxProductsShown != 0) {
        section.params.maxProductsShown = setupParams.maxProductsShown;
    }

    if (['products_with_slider', 'products'].includes(setupParams.sectionType)) {
        section.params.showProductsWithoutStock = setupParams.showProductsWithoutStock;
        section.params.showUnstartedAuctions = setupParams.showUnstartedAuctions;
        section.params.showEndedAuctions = setupParams.showEndedAuctions;
    }

    if (setupParams.lexicalContent) {
        let configurationKey;

        if (setupParams.sectionType === 'text') {
            configurationKey = 'sectionText_' + pageId + '_' + sectionId;
        } else if (setupParams.sectionType === 'products_with_slider') {
            configurationKey = 'section_products_with_slider_' + pageId + '_' + sectionId + '_' + setupParams.lastProductPassed.id
        }

        publishConfiguration(setupParams.lexicalContent, getConfigurationKey(configurationKey),
            () => {
                console.log('lexicalContent saved to Nostr relay!!');
            });
    }

    NostrGlobalConfigFireReactivity();

    saveContentToNostr();
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

export function getAppRoutes() {
    return Object.keys(pagesAndTitles);
}

/*
Parses some known tags from rich texts
(like \n\n) and prints the equivalent HTML
*/
export function getHtmlFromRichText(richText: string) {
    return DOMPurify.sanitize(richText)
        //.replace(/^### (.*$)/gim, '<h3>$1</h3>') // h3 tag
        //.replace(/^## (.*$)/gim, '<h2>$1</h2>') // h2 tag
        //.replace(/^# (.*$)/gim, '<h11>$1</h11>') // h1 tag
        .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
        .replace(/\*(.*)\*/gim, '<i>$1</i>')
        .replace(/^([^\n]+)\n/gim, '<p class="my-0">$1</p>')
        .replace(/\n\n([^\n]+)\n/gim, '<p class="my-0 mt-1">$1</p>')
        .replace(/\n([^\n]+)\n/gim, '<p class="my-0">$1</p>');
}