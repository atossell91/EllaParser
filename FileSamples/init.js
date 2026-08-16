import { {{appName}} } from '{{appJsPath}}'

function init() {
    const app = new {{appName}}();
    // app.run();
}

document.addEventListener("DOMContentLoaded", () => {
    init();
});
