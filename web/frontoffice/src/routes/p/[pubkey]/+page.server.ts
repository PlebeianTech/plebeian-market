
export async function load({ params }) {
    const { pubkey } = params;
    return { pubkey };
}
