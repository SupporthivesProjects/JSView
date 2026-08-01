import{r as t}from"./index-D-jrKfTQ.js";function c(o=!1,r={}){const[s,n]=t.useState(o),u=t.useCallback(()=>{n(e=>e||(r.onOpen?.(),!0))},[r.onOpen]),l=t.useCallback(()=>{n(e=>e&&(r.onClose?.(),!1))},[r.onClose]);return[s,{open:u,close:l,toggle:t.useCallback(()=>{s?l():u()},[l,u,s]),set:n}]}export{c as u};
//# sourceMappingURL=use-disclosure-Bci3svmK.js.map
