export function load({ params }) {
    const { nym } = params;
    return { stallOwnerNym: nym };
}
