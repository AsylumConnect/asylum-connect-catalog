var mobileBreakpoint='768px';var tabletBreakpoint='992px';var smallMonitorBreakpoint='1200px';$(document).ready(function(){$('.message .close').on('click',function(){$(this).parent().fadeOut();});$('#open-nav').on('click',function(){$('.mobile.only .vertical.menu').transition('slide down');});$('.dropdown').dropdown();$('select').dropdown();});(function($){function icontains(elem,text){return(elem.textContent||elem.innerText||$(elem).text()||"").toLowerCase().indexOf((text||"").toLowerCase())>-1;}
$.expr[':'].icontains=$.expr.createPseudo?$.expr.createPseudo(function(text){return function(elem){return icontains(elem,text);};}):function(elem,i,match){return icontains(elem,match[3]);};})(jQuery);var currentState=[];function changeMenu(e){var children=$($(e).children()[1]).html();children+='<a class="item" onClick="back()">Back</a><i class="back icon"></i>';currentState.push($('.mobile.only .vertical.menu').html());$('.mobile.only .vertical.menu').html(children);}
function back(){$('.mobile.only .vertical.menu').html(currentState.pop());}