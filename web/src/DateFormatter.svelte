<script>
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    export let date = null;
</script>

<span>{weekdays[date.getDay()]} {date.toLocaleString('default', { month: 'long' })} {date.getDate()}, {date.getHours()}:{date.getMinutes()}</span>
