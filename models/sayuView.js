import { sayuView } from "./models/sayuView.js"

export class sayu {
    #viewElement;

    constructor() {
        const viewRes = sayuView();
        this.#viewElement = viewRes.elems
    }
}
