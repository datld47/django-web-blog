
function get_uct_time_from_local_input(inputId) {
    const localDateStr = document.getElementById(inputId).value;
    if (!localDateStr) return null;
    // Parse local datetime string (ví dụ: "2025-07-18T14:30")
    const localDate = new Date(localDateStr);
    // Chuyển sang UTC ISO string (ví dụ: "2025-07-18T07:30:00.000Z")
    return localDate.toISOString();
}

function convert_uct_to_local_time(utcStr) {
    if (!utcStr) return '';
        const localDate = new Date(utcStr);
        const localStr = localDate.toLocaleString("vi-VN", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
       return localStr;      
}

function convert_class_uct_time_to_local_time() {
    $('.utc-time').each(function () {
        const utcStr = $(this).data('utc');
        const localStr= convert_uct_to_local_time(utcStr);
        if(localStr)
        {
            $(this).text(localStr);
        }
    });
}
