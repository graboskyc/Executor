// web component
class TemplateBox extends HTMLElement {
  
    constructor() {
        super();
        this.title = 'Sample Template';
        this.engine = 'python3';
        this.icon = "question_mark";
    }

    static observedAttributes = ['title', 'engine', 'icon'];

    attributeChangedCallback(property, oldValue, newValue) {
        if (oldValue != newValue) {
            this[ property ] = newValue;
            //console.log(`Attribute ${property} has changed from ${oldValue} to ${newValue}.`);
            this.connectedCallback();
        }
    }

    connectedCallback() {
      this.innerHTML = `
        <li class="tb_li">
        <div class='grid'>
            <div class="material-symbols-outlined tb_circle">${this.icon}</div>
            <div class="tb_title">${this.title}</div>
        </div>
        </li>
      `
    }
    
  }
  
  // register component
  customElements.define('template-box', TemplateBox );