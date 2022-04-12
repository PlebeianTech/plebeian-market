import Auction from './Auction.svelte';

const target = document.querySelector('#plebeian-auction');
const auction = new Auction({ target, props: { key: target.dataset.key } });

export default auction;