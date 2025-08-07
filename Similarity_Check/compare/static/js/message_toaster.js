function showToast(message, type, options = {}) {
    const defaultOptions = {
        positionClass: "toast-top-right",
        timeOut: 5000,
        closeButton: true,
        progressBar: true,
    };
    const settings = { ...defaultOptions, ...options };
    toastr.options = settings;

    switch (type) {
        case 'success':
            toastr.success(message);
            break;
        case 'error':
            toastr.error(message);
            break;
        case 'warning':
            toastr.warning(message);
            break;
        case 'info':
            toastr.info(message);
            break;
        default:
            console.warn("Unknown toast type:", type);
            toastr.info(message);
            break;
    }
}
