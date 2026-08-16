import { {{viewName}} } from "{{viewPath}}"

export class {{modelName}} {
    #viewElement;

    constructor() {
        const viewRes = {{viewName}}();
        this.#viewElement = viewRes.elems
    }
}
