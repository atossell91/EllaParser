import { {{viewName}} } from "{{viewPath}}"

export class {{modelName}} {
    #view;

    constructor() {
        this.#view = new {{viewName}}();
    }

    get viewRoot() {
        return this.#view.refRoot;
    }
}
