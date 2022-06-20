<script lang="ts">
    // code taken from https://victordiego.com/lightbox/ adapted for our needs and made into a Svelte component

    import type { Media } from "../types/auction";

    export let photos : Media[];

    let animation = {
        fadeIn: 'fadeIn .3s',
        fadeOut: 'fadeOut .3s',
        scaleIn: 'createBox .3s',
        scaleOut: 'deleteBox .3s'
    };

    var btnClose, btnNav, currentItem, container, content, wrapper, currentTrigger;

    function sortContent(content) {
        let href = content.getAttribute('href') || content.getAttribute('src');

        if (href.match(/\.(jpeg|jpg|gif|png)/)) {
            let image = document.createElement('img');
            image.className = 'lightbox-image';
            image.src = href;
            image.alt = content.getAttribute('data-image-alt');
            return image;
        }

        return content.cloneNode(true);
    }

    function galleryItems(element) {
        let items = {
            next: element.parentElement.parentElement.nextElementSibling,
            previous: element.parentElement.parentElement.previousElementSibling
        };
        for (const key in items) {
            if (items[key] !== null) {
                items[key] = items[key].querySelector('[data-lightbox]');
            }
        }
        return items;
    }

    function buildLightbox(element) {
        element.blur();
        currentItem = element;
        element.classList.add('current-lightbox-item');

        btnClose = document.createElement('button');
        btnClose.className = 'lightbox-btn lightbox-btn-close';

        content = document.createElement('div');
        content.className = 'lightbox-content';
        content.appendChild(sortContent(element));

        wrapper = content.cloneNode(false);
        wrapper.className = 'lightbox-wrapper';
        wrapper.style.animation = [animation.scaleIn, animation.fadeIn];
        wrapper.appendChild(content);
        wrapper.appendChild(btnClose);

        container = content.cloneNode(false);
        container.className = 'lightbox-container';
        container.style.animation = animation.fadeIn;
        container.onclick = function() {};
        container.appendChild(wrapper);

        if (element.getAttribute('data-lightbox') === 'gallery') {
            container.classList.add('lightbox-gallery');
            btnNav = {next: '', previous: ''};
            for (const key in btnNav) {
                if (btnNav.hasOwnProperty(key)) {
                    btnNav[key] = btnClose.cloneNode(false);
                    btnNav[key].className = 'lightbox-btn lightbox-btn-' + key;
                    btnNav[key].disabled = galleryItems(element)[key] === null;
                    wrapper.appendChild(btnNav[key]);
                }
            }
        }

        document.body.appendChild(container);
        document.body.classList.toggle('remove-scroll');
    }

    function galleryNavigation(position) {
        wrapper.removeAttribute('style');
        var item = galleryItems(currentItem)[position];
        if (item !== null) {
            content.style.animation = animation.fadeOut;
            setTimeout(function () {
                content.replaceChild(sortContent(item), content.children[0]);
                content.style.animation = animation.fadeIn;
            }, 200);
            currentItem.classList.remove('current-lightbox-item');
            item.classList.add('current-lightbox-item');
            currentItem = item;
            for (const key in btnNav) {
                if (btnNav.hasOwnProperty(key)) {
                    btnNav[key].disabled = galleryItems(item)[key] === null ? true : false;
                }
            }
        }
    }

    function closeLightbox() {
        container.style.animation = animation.fadeOut;
        wrapper.style.animation = [animation.scaleOut, animation.fadeOut];
        setTimeout(function () {
            if (document.body.contains(container)) {
                document.body.removeChild(container);
                currentTrigger.focus();
                currentItem.classList.remove('current-lightbox-item');
                document.body.classList.toggle('remove-scroll');
            }
        }, 200);
    }

    ['click', 'keyup'].forEach( function (eventType) {
        document.body.addEventListener(eventType, function (event) {
            let kevent: KeyboardEvent = <KeyboardEvent>event;
            if (document.body.contains(container)) {
                var target = event.target,
                    type = event.type;
                if ([container, btnClose].indexOf(target) !== -1 || kevent.key === "Escape") {
                    closeLightbox();
                }
                if (container.classList.contains('lightbox-gallery')) {
                    if ((target === btnNav.next && type === 'click') || kevent.key === "ArrowRight") {
                        galleryNavigation('next');
                    }
                    if ((target === btnNav.previous && type === 'click') || kevent.key === "ArrowLeft") {
                        galleryNavigation('previous');
                    }
                }
            }
        });
    });

    function click(e) {
        buildLightbox(e.target);
        currentTrigger = e.target;
    }
</script>

<style global>
.remove-scroll {
  overflow: hidden;
}

.lightbox-hide {
  top: -9999px;
  left: -9999px;
  position: absolute;
  visibility: hidden;
}

.lightbox-container {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 2em;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  position: fixed;
  align-items: center;
  justify-content: center;
  background-color: rgb(29, 29, 29);
  background-color: rgba(29, 29, 29, 0.8);
  z-index: 100;
}

.lightbox-wrapper {
  position: relative;
}

.lightbox-image {
  max-height: 100vh;
  vertical-align: middle;
}

.lightbox-btn {
  width: 2.2em;
  height: 2.2em;
  position: absolute;
  border-radius: 50%;
  transition: all 0.3s;
  background-color: #ff00ff;
  background-position: center;
  background-repeat: no-repeat;
}

.lightbox-btn:disabled {
  display: none;
}

.lightbox-btn-close {
  top: -0.8em;
  right: -0.8em;
  background-size: 40%;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="rgb(255,255,255)" d="M98.2 89.3L58.8 50l39.3-39.3c2.4-2.4 2.4-6.4 0-8.8-2.4-2.4-6.4-2.4-8.8 0L50 41.2 10.7 1.8C8.3-.6 4.3-.6 1.9 1.8c-2.4 2.4-2.4 6.4 0 8.8L41.2 50 1.8 89.3c-2.4 2.4-2.4 6.4 0 8.8 2.4 2.4 6.4 2.4 8.8 0L50 58.8l39.3 39.3c2.4 2.4 6.4 2.4 8.8 0 2.5-2.4 2.5-6.3.1-8.8z"/></svg>');
}

.lightbox-btn-next,
.lightbox-btn-previous {
  top: calc(50% - (2.2em / 2));
  background-size: 25% 80%;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 17 31" ><path fill="rgb(255,255,255)" d="M0.5,27.9c-0.7,0.7-0.7,1.7,0,2.4c0.7,0.7,1.7,0.7,2.4,0l13.6-13.6c0.7-0.7,0.7-1.7,0-2.4L2.9,0.7 C2.2,0,1.2,0,0.5,0.7c-0.7,0.7-0.7,1.7,0,2.4l12.4,12.4L0.5,27.9z"/></svg>');
}

.lightbox-btn-previous {
  left: 1.5em;
  transform: rotate(180deg);
}

.lightbox-btn-next {
  right: 1.5em;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes createBox {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

@keyframes deleteBox {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(0);
  }
}
</style>

<div class="gallery lg:w-4/5 grid grid-cols-2 gap-2 m-auto">
    {#each photos as photo, i}
            {#if i < 2}
                <div class="gallery-item h-auto hover:scale-110 hover:-translate-y-1 table">
            <a class="table-cell align-bottom" href={photo.url} on:click|preventDefault={event => click(event)}>
                <img class="rounded-md" data-lightbox="gallery" src={photo.url} alt="Auctioned item" />
            </a>
                </div>
                {:else}
                <div class="gallery-item h-40 hover:scale-110 hover:translate-y-1 table">
                <a class="table-cell align-top" href={photo.url} on:click|preventDefault={event => click(event)}>
                    <img class="rounded-md" data-lightbox="gallery" src={photo.url} alt="Auctioned item" />
                </a>
                </div>
                {/if}
    {/each}
</div>
