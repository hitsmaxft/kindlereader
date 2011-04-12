// DEFLATE, base64 by Dan Kogai http://github.com/dankogai/
(function(){var V=function(){for(var f=[],n="A".charCodeAt(0),m="a".charCodeAt(0),i="0".charCodeAt(0),k=0;k<26;k++)f.push(n+k);for(k=0;k<26;k++)f.push(m+k);for(k=0;k<10;k++)f.push(i+k);f.push("+".charCodeAt(0));f.push("/".charCodeAt(0));return f}(),E=function(f){for(var n={},m=0,i=f.length;m<i;m++)n[f.charAt(m)]=m;return n}("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"),q=function(f){for(var n=[],m=0,i=f.length;m<i;m++)n[m]=f.charCodeAt(m);return n},O=function(f){for(var n=0;f.length%
3;){f.push(0);n++}for(var m=[],i=0,k=f.length;i<k;i+=3){var h=f[i],K=f[i+1],F=f[i+2];if(h>=256||K>=256||F>=256)throw"unsupported character found";h=h<<16|K<<8|F;m.push(V[h>>>18],V[h>>>12&63],V[h>>>6&63],V[h&63])}for(;n--;)m[m.length-n-1]="=".charCodeAt(0);return String.fromCharCode.apply(String,m)},W=function(f){f=f.replace(/[^A-Za-z0-9+\/]+/g,"");for(var n=[],m=f.length%4,i=0,k=f.length;i<k;i+=4){var h=(E[f.charAt(i)]||0)<<18|(E[f.charAt(i+1)]||0)<<12|(E[f.charAt(i+2)]||0)<<6|(E[f.charAt(i+3)]||
0);n.push(h>>16,h>>8&255,h&255)}n.length-=[0,0,2,1][m];return n},B=function(f){for(var n=[],m=0,i=f.length;m<i;m++){var k=f[m];if(k<128)n.push(k);else k<2048?n.push(192|k>>>6,128|k&63):n.push(224|k>>>12&15,128|k>>>6&63,128|k&63)}return n},u=function(f){for(var n=[],m=0,i=f.length;m<i;m++){var k=f[m];if(k<128)n.push(k);else{var h=f[++m];if(k<224)n.push((k&31)<<6|h&63);else{var K=f[++m];n.push((k&15)<<12|(h&63)<<6|K&63)}}}return n},v=function(f){return O(q(f))},X=function(f){return String.fromCharCode.apply(String,
W(f))},j=function(f){return String.fromCharCode.apply(String,u(f))},Y=function(f){return String.fromCharCode.apply(String,u(q(f)))},Z=function(f){return B(q(f))},y=function(f){return String.fromCharCode.apply(String,B(q(f)))};if(window.btoa)var G=window.btoa,x=function(f){return G(y(f))};else{G=v;x=function(f){return O(Z(f))}}if(window.atob)var C=window.atob,z=function(f){return Y(C(f))};else{C=X;z=function(f){return j(W(f))}}window.Base64={convertUTF8ArrayToBase64:O,convertByteArrayToBase64:O,convertBase64ToUTF8Array:W,
convertBase64ToByteArray:W,convertUTF16ArrayToUTF8Array:B,convertUTF16ArrayToByteArray:B,convertUTF8ArrayToUTF16Array:u,convertByteArrayToUTF16Array:u,convertUTF8StringToBase64:v,convertBase64ToUTF8String:X,convertUTF8StringToUTF16Array:function(f){return u(q(f))},convertUTF8ArrayToUTF16String:j,convertByteArrayToUTF16String:j,convertUTF8StringToUTF16String:Y,convertUTF16StringToUTF8Array:Z,convertUTF16StringToByteArray:Z,convertUTF16ArrayToUTF8String:function(f){return String.fromCharCode.apply(String,
B(f))},convertUTF16StringToUTF8String:y,convertUTF16StringToBase64:x,convertBase64ToUTF16String:z,fromBase64:X,toBase64:v,atob:C,btoa:G,utob:y,btou:Y,encode:x,encodeURI:function(f){return x(f).replace(/[+\/]/g,function(n){return n=="+"?"-":"_"}).replace(/=+$/,"")},decode:function(f){return z(f.replace(/[-_]/g,function(n){return n=="-"?"+":"/"}))}}})();
(function(){var V=parseInt(5),E,q,O,W,B=null,u,v,X,j,Y,Z,y,G,x,C,z,f,n,m,i,k,h,K,F,t,Ga,va,$,Ha,L,P,Q,aa,w,H,I,R,A,r,S,ca,M,ea,ba,wa,ja,ka,T,la,xa,fa,ma,da,na,oa,ya,ga=function(){this.dl=this.fc=0},za=function(){this.extra_bits=this.static_tree=this.dyn_tree=null;this.max_code=this.max_length=this.elems=this.extra_base=0},N=function(c,e,b,a){this.good_length=c;this.max_lazy=e;this.nice_length=b;this.max_chain=a},Ua=function(){this.next=null;this.len=0;this.ptr=Array(8192);this.off=0},Aa=[0,0,0,0,
0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],ha=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],Va=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],Ia=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],Ba=[new N(0,0,0,0),new N(4,4,8,4),new N(4,5,16,8),new N(4,6,32,32),new N(4,4,16,16),new N(8,16,32,32),new N(8,16,128,128),new N(8,32,128,256),new N(32,128,258,1024),new N(32,258,258,4096)],pa=function(c){B[v+u++]=c;if(v+u==8192)if(u!=0){var e;if(E!=null){c=E;E=E.next}else c=new Ua;
c.next=null;c.len=c.off=0;c=c;if(q==null)q=O=c;else O=O.next=c;c.len=u-v;for(e=0;e<c.len;e++)c.ptr[e]=B[v+e];u=v=0}},qa=function(c){c&=65535;if(v+u<8190){B[v+u++]=c&255;B[v+u++]=c>>>8}else{pa(c&255);pa(c>>>8)}},ra=function(){z=(z<<V^j[h+3-1]&255)&8191;f=y[32768+z];y[h&32767]=f;y[32768+z]=h},U=function(c,e){D(e[c].fc,e[c].dl)},Ja=function(c,e,b){return c[e].fc<c[b].fc||c[e].fc==c[b].fc&&M[e]<=M[b]},Ka=function(c,e,b){var a;for(a=0;a<b&&ya<oa.length;a++)c[e+a]=oa.charCodeAt(ya++)&255;return a},La=function(c){var e=
Ga,b=h,a,d=k,g=h>32506?h-32506:0,l=h+258,o=j[b+d-1],p=j[b+d];if(k>=Ha)e>>=2;do{a=c;if(!(j[a+d]!=p||j[a+d-1]!=o||j[a]!=j[b]||j[++a]!=j[b+1])){b+=2;a++;do;while(j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&j[++b]==j[++a]&&b<l);a=258-(l-b);b=l-258;if(a>d){K=c;d=a;if(a>=258)break;o=j[b+d-1];p=j[b+d]}}}while((c=y[c&32767])>g&&--e!=0);return d},Ca=function(){var c,e,b=65536-t-h;if(b==-1)b--;else if(h>=65274){for(c=0;c<32768;c++)j[c]=j[c+
32768];K-=32768;h-=32768;C-=32768;for(c=0;c<8192;c++){e=y[32768+c];y[32768+c]=e>=32768?e-32768:0}for(c=0;c<32768;c++){e=y[c];y[c]=e>=32768?e-32768:0}b+=32768}if(!F){c=Ka(j,h+t,b);if(c<=0)F=true;else t+=c}},Wa=function(c,e,b){var a;if(!W){if(!F){x=G=0;var d,g;if(aa[0].dl==0){H.dyn_tree=L;H.static_tree=Q;H.extra_bits=Aa;H.extra_base=257;H.elems=286;H.max_length=15;H.max_code=0;I.dyn_tree=P;I.static_tree=aa;I.extra_bits=ha;I.extra_base=0;I.elems=30;I.max_length=15;I.max_code=0;R.dyn_tree=w;R.static_tree=
null;R.extra_bits=Va;R.extra_base=0;R.elems=19;R.max_length=7;for(g=d=R.max_code=0;g<28;g++){wa[g]=d;for(a=0;a<1<<Aa[g];a++)ea[d++]=g}ea[d-1]=g;for(g=d=0;g<16;g++){ja[g]=d;for(a=0;a<1<<ha[g];a++)ba[d++]=g}for(d>>=7;g<30;g++){ja[g]=d<<7;for(a=0;a<1<<ha[g]-7;a++)ba[256+d++]=g}for(a=0;a<=15;a++)A[a]=0;for(a=0;a<=143;){Q[a++].dl=8;A[8]++}for(;a<=255;){Q[a++].dl=9;A[9]++}for(;a<=279;){Q[a++].dl=7;A[7]++}for(;a<=287;){Q[a++].dl=8;A[8]++}Ma(Q,287);for(a=0;a<30;a++){aa[a].dl=5;aa[a].fc=Na(a,5)}Oa()}for(a=
0;a<8192;a++)y[32768+a]=0;va=Ba[$].max_lazy;Ha=Ba[$].good_length;Ga=Ba[$].max_chain;C=h=0;t=Ka(j,0,65536);if(t<=0){F=true;t=0}else{for(F=false;t<262&&!F;)Ca();for(a=z=0;a<2;a++)z=(z<<V^j[a]&255)&8191}q=null;v=u=0;if($<=3){k=2;i=0}else{i=2;m=0}X=false}W=true;if(t==0){X=true;return 0}}if((a=Pa(c,e,b))==b)return b;if(X)return a;if($<=3)for(;t!=0&&q==null;){ra();if(f!=0&&h-f<=32506){i=La(f);if(i>t)i=t}if(i>=3){g=ia(h-K,i-3);t-=i;if(i<=va){i--;do{h++;ra()}while(--i!=0);h++}else{h+=i;i=0;z=j[h]&255;z=(z<<
V^j[h+1]&255)&8191}}else{g=ia(0,j[h]&255);t--;h++}if(g){sa(0);C=h}for(;t<262&&!F;)Ca()}else for(;t!=0&&q==null;){ra();k=i;n=K;i=2;if(f!=0&&k<va&&h-f<=32506){i=La(f);if(i>t)i=t;i==3&&h-K>4096&&i--}if(k>=3&&i<=k){g=ia(h-1-n,k-3);t-=k-1;k-=2;do{h++;ra()}while(--k!=0);m=0;i=2;h++;if(g){sa(0);C=h}}else{if(m!=0){if(ia(0,j[h-1]&255)){sa(0);C=h}}else m=1;h++;t--}for(;t<262&&!F;)Ca()}if(t==0){m!=0&&ia(0,j[h-1]&255);sa(1);X=true}return a+Pa(c,a+e,b-a)},Pa=function(c,e,b){var a,d,g;for(a=0;q!=null&&a<b;){d=
b-a;if(d>q.len)d=q.len;for(g=0;g<d;g++)c[e+a+g]=q.ptr[q.off+g];q.off+=d;q.len-=d;a+=d;if(q.len==0){d=q;q=q.next;d=d;d.next=E;E=d}}if(a==b)return a;if(v<u){d=b-a;if(d>u-v)d=u-v;for(g=0;g<d;g++)c[e+a+g]=B[v+g];v+=d;a+=d;if(u==v)u=v=0}return a},Oa=function(){var c;for(c=0;c<286;c++)L[c].fc=0;for(c=0;c<30;c++)P[c].fc=0;for(c=0;c<19;c++)w[c].fc=0;L[256].fc=1;fa=T=la=xa=da=na=0;ma=1},Da=function(c,e){for(var b=r[e],a=e<<1;a<=S;){a<S&&Ja(c,r[a+1],r[a])&&a++;if(Ja(c,b,r[a]))break;r[e]=r[a];e=a;a<<=1}r[e]=
b},Ma=function(c,e){var b=Array(16),a=0,d;for(d=1;d<=15;d++){a=a+A[d-1]<<1;b[d]=a}for(a=0;a<=e;a++){d=c[a].dl;if(d!=0)c[a].fc=Na(b[d]++,d)}},Fa=function(c){var e=c.dyn_tree,b=c.static_tree,a=c.elems,d,g=-1,l=a;S=0;ca=573;for(d=0;d<a;d++)if(e[d].fc!=0){r[++S]=g=d;M[d]=0}else e[d].dl=0;for(;S<2;){d=r[++S]=g<2?++g:0;e[d].fc=1;M[d]=0;da--;if(b!=null)na-=b[d].dl}c.max_code=g;for(d=S>>1;d>=1;d--)Da(e,d);do{d=r[1];r[1]=r[S--];Da(e,1);b=r[1];r[--ca]=d;r[--ca]=b;e[l].fc=e[d].fc+e[b].fc;M[l]=M[d]>M[b]+1?M[d]:
M[b]+1;e[d].dl=e[b].dl=l;r[1]=l++;Da(e,1)}while(S>=2);r[--ca]=r[1];l=c.dyn_tree;d=c.extra_bits;a=c.extra_base;b=c.max_code;var o=c.max_length,p=c.static_tree,J,s,ta,Ea,ua=0;for(s=0;s<=15;s++)A[s]=0;l[r[ca]].dl=0;for(c=ca+1;c<573;c++){J=r[c];s=l[l[J].dl].dl+1;if(s>o){s=o;ua++}l[J].dl=s;if(!(J>b)){A[s]++;ta=0;if(J>=a)ta=d[J-a];Ea=l[J].fc;da+=Ea*(s+ta);if(p!=null)na+=Ea*(p[J].dl+ta)}}if(ua!=0){do{for(s=o-1;A[s]==0;)s--;A[s]--;A[s+1]+=2;A[o]--;ua-=2}while(ua>0);for(s=o;s!=0;s--)for(J=A[s];J!=0;){d=r[--c];
if(!(d>b)){if(l[d].dl!=s){da+=(s-l[d].dl)*l[d].fc;l[d].fc=s}J--}}}Ma(e,g)},Qa=function(c,e){var b,a=-1,d,g=c[0].dl,l=0,o=7,p=4;if(g==0){o=138;p=3}c[e+1].dl=65535;for(b=0;b<=e;b++){d=g;g=c[b+1].dl;if(!(++l<o&&d==g)){if(l<p)w[d].fc+=l;else if(d!=0){d!=a&&w[d].fc++;w[16].fc++}else if(l<=10)w[17].fc++;else w[18].fc++;l=0;a=d;if(g==0){o=138;p=3}else if(d==g){o=6;p=3}else{o=7;p=4}}}},Ra=function(c,e){var b,a=-1,d,g=c[0].dl,l=0,o=7,p=4;if(g==0){o=138;p=3}for(b=0;b<=e;b++){d=g;g=c[b+1].dl;if(!(++l<o&&d==
g)){if(l<p){do U(d,w);while(--l!=0)}else if(d!=0){if(d!=a){U(d,w);l--}U(16,w);D(l-3,2)}else if(l<=10){U(17,w);D(l-3,3)}else{U(18,w);D(l-11,7)}l=0;a=d;if(g==0){o=138;p=3}else if(d==g){o=6;p=3}else{o=7;p=4}}}},sa=function(c){var e,b,a,d;d=h-C;ka[xa]=fa;Fa(H);Fa(I);Qa(L,H.max_code);Qa(P,I.max_code);Fa(R);for(a=18;a>=3;a--)if(w[Ia[a]].dl!=0)break;da+=3*(a+1)+5+5+4;a=a;e=da+3+7>>3;b=na+3+7>>3;if(b<=e)e=b;if(d+4<=e&&C>=0){D(0+c,3);Sa();qa(d);qa(~d);for(a=0;a<d;a++)pa(j[C+a])}else if(b==e){D(2+c,3);Ta(Q,
aa)}else{D(4+c,3);d=H.max_code+1;e=I.max_code+1;a=a+1;D(d-257,5);D(e-1,5);D(a-4,4);for(b=0;b<a;b++)D(w[Ia[b]].dl,3);Ra(L,d-1);Ra(P,e-1);Ta(L,P)}Oa();c!=0&&Sa()},ia=function(c,e){Z[T++]=e;if(c==0)L[e].fc++;else{c--;L[ea[e]+256+1].fc++;P[(c<256?ba[c]:ba[256+(c>>7)])&255].fc++;Y[la++]=c;fa|=ma}ma<<=1;if((T&7)==0){ka[xa++]=fa;fa=0;ma=1}if($>2&&(T&4095)==0){var b=T*8,a=h-C,d;for(d=0;d<30;d++)b+=P[d].fc*(5+ha[d]);b>>=3;if(la<parseInt(T/2)&&b<parseInt(a/2))return true}return T==8191||la==8192},Ta=function(c,
e){var b,a=0,d=0,g=0,l=0,o,p;if(T!=0){do{if((a&7)==0)l=ka[g++];b=Z[a++]&255;if((l&1)==0)U(b,c);else{o=ea[b];U(o+256+1,c);p=Aa[o];if(p!=0){b-=wa[o];D(b,p)}b=Y[d++];o=(b<256?ba[b]:ba[256+(b>>7)])&255;U(o,e);p=ha[o];if(p!=0){b-=ja[o];D(b,p)}}l>>=1}while(a<T)}U(256,c)},D=function(c,e){if(x>16-e){G|=c<<x;qa(G);G=c>>16-x;x+=e-16}else{G|=c<<x;x+=e}},Na=function(c,e){var b=0;do{b|=c&1;c>>=1;b<<=1}while(--e>0);return b>>1},Sa=function(){if(x>8)qa(G);else x>0&&pa(G);x=G=0};window.RawDeflate||(RawDeflate={});
RawDeflate.deflate=function(c,e){var b,a;oa=c;ya=0;if(typeof e=="undefined")e=6;if(b=e)if(b<1)b=1;else{if(b>9)b=9}else b=6;$=b;F=W=false;if(B==null){E=q=O=null;B=Array(8192);j=Array(65536);Y=Array(8192);Z=Array(32832);y=Array(65536);L=Array(573);for(b=0;b<573;b++)L[b]=new ga;P=Array(61);for(b=0;b<61;b++)P[b]=new ga;Q=Array(288);for(b=0;b<288;b++)Q[b]=new ga;aa=Array(30);for(b=0;b<30;b++)aa[b]=new ga;w=Array(39);for(b=0;b<39;b++)w[b]=new ga;H=new za;I=new za;R=new za;A=Array(16);r=Array(573);M=Array(573);
ea=Array(256);ba=Array(512);wa=Array(29);ja=Array(30);ka=Array(parseInt(1024))}for(var d=Array(1024),g=[];(b=Wa(d,0,d.length))>0;){var l=Array(b);for(a=0;a<b;a++)l[a]=String.fromCharCode(d[a]);g[g.length]=l.join("")}oa=null;return g.join("")}})();


var bodyipb414353, _greaderipb414353;

function jbsipb414353(html)
{
    html = html.replace(/<!--.*?-->/ig, '');    
        if (html.length > 384000) return html; /* too big to deflate quickly */
    var def = Base64.convertUTF8StringToBase64(RawDeflate.deflate(unescape(encodeURIComponent(html))));
    if (def.length >= 65536) return html; /* bug, these libs stop at 64K */
    return '<' + '![D[' + Base64.convertUTF8StringToBase64(RawDeflate.deflate(unescape(encodeURIComponent(html))));        
}

function _ipSendipb414353(href, title)
{
    var d=document,
        l=d.location,
        e=window.getSelection,
        k=d.getSelection,
        x=d.selection,
        s=String(e? e(): (k)? k(): (x?x.createRange().text: '')),
        e=encodeURIComponent,
        z=d.createElement('scr'+'ipt'),
        p='a=&k=swdnfEqUFHRN&u=' + e(href) + '&t=' + e(title) + '&s=' + e(s.length < 10240 ? s : '');
    
        var b = _greaderipb414353 ? '' : jbsipb414353(bodyipb414353);
        if (b.length > 256000) b = '';
    
    i=document.createElement('iframe');
    i.setAttribute('name', 'ipb414353');
    i.setAttribute('id', 'ipb414353');
    c = 'left:10px;top:10px;width:168px;';
    i.setAttribute('style', 'z-index: 2147483647; position: fixed;'+c+'width:168px;height: 100px; border: 3px solid #aaa;');
    document.body.appendChild(i);
    i.onload = function(){ setTimeout(_clipb414353_close, 350); }

    window['ipb414353'].document.write(
        '<html><body style="color: #555; background-color: #fff; text-align: center; margin: 0px; font-family: Georgia, Times, serif; font-size: 26px;">' +
        '<img style="display: block; position: fixed; bottom: 4px; left: 72px;" src="data:image/gif;base64,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"/>' +
        '<div style="text-align: center; width: 80%; padding-bottom: 1px; margin: 0 auto 15px auto; font-size: 14px; border-bottom: 1px solid #ccc; color: #333;">dogear</div>' +
        'Saving...' +
        '<form action="' + document.location.protocol + '//reader.dogear.mobi/post_v1" method="post" id="f" accept-charset="utf-8">' +
        '<input type="hidden" name="k" value="{{ key }}"/>' +
        '<input type="hidden" name="u" value="'+href+'"/>' +
        '<input type="hidden" name="t" value="'+title+'"/>' +
        '<input type="hidden" name="p" value="'+p+'"/>' +
        '<input type="hidden" name="b" id="b" value=""/>' +
        '</form>' +
        '<scr'+'ipt>setTimeout(function() { document.getElementById("b").value = decodeURIComponent("'+e(b)+'"); document.getElementById("f").submit(); }, 1);</scr'+'ipt>' +
        '</body></html>'
    );
}

function _rlipb414353(){var title,d=document,l=d.location,href=l.href;
d.title = title = d.title.substring(12);
if (href == 'http://reader.dogear.mobi/i4' || typeof iptstbt != 'undefined') { alert("The bookmarklet is correctly installed."); throw(0); }


/* Google Reader parsing code by Pascal Lalibert茅 */
if (/www\.google\.[^/]+\/reader\/i\//.test(d.location)) {
    _greaderipb414353 = true;
        if (typeof(window.iprl5) != 'function') { 
        if (confirm("The Google Reader-compatible Instapaper bookmarklet is not installed.\n\nWould you like to go to Instapaper now to install it?")) {
            window.location.href = "http://reader.dogear.mobi/u";
        }
        return;
    }
    var n = d.getElementById('entries').childNodes,
    l = null,
    h = null;
    for (var i = 0; i < n.length; i++) {
        if (/expanded/.test(n[i].className)) {
            l = n[i];
            break;
        }
    }
    var t = l.getElementsByTagName('span');
    for (var i = 0; i < t.length; i++) {
        if (/item-title/.test(t[i].className)) {
            title = t[i].textContent;
            break;
        }
    }
    var h = l.getElementsByTagName('a');
    for (var i = h.length - 1; i >= 0; i--) {
        if (/See original/.test(h[i].textContent) && h[i].href) {
            href = h[i].href;
            break;
        }
        if (/item-title-link/.test(h[i].className) && h[i].href) {
            href = h[i].href;
            break;
        }        
    }
} else if (/www\.google\.[^/]+\/reader/.test(d.location) && typeof(window.getPermalink) == 'function' && getPermalink() != null) {
    _greaderipb414353 = true;
        if (typeof(window.iprl5) != 'function') { 
        if (confirm("The Google Reader-compatible Instapaper bookmarklet is not installed.\n\nWould you like to go to Instapaper now to install it?")) {
            window.location.href = "http://reader.dogear.mobi/u";
        }
        return;
    }
    var l = getPermalink();
    href = l.url;
    title=l.title;
}

if (! _greaderipb414353) {
    try{
        function ipReadabilityCompleted(bodyNode)
        {
            bodyipb414353 = bodyNode.innerHTML;
            _ipSendipb414353(document.location.href, document.title);
        }
        
        /*
 * Readability. An Arc90 Lab Experiment. 
 * Website: http://lab.arc90.com/experiments/readability
 * Source:  http://code.google.com/p/arc90labs-readability
 *
 * "Readability" is a trademark of Arc90 Inc and may not be used without explicit permission. 
 *
 * Copyright (c) 2010 Arc90 Inc
 * Readability is licensed under the Apache License, Version 2.0.
 * 
 * This version has been modified by Instapaper, LLC.
 * Uncompressed source of the modified version is available at:
 *   http://www.instapaper.com/javascript/ipreadability-1.7.1.js
**/
var readability={version:"1.7.1",convertLinksToFootnotes:false,reversePageScroll:false,biggestFrame:false,flags:7,documentNode:null,bodyNode:null,fetchMultiplePages:true,pageBodies:[],ajaxIsRunning:false,FLAG_STRIP_UNLIKELYS:1,FLAG_WEIGHT_CLASSES:2,FLAG_CLEAN_CONDITIONALLY:4,maxPages:30,parsedPages:{},pageETags:{},regexps:{unlikelyCandidates:/combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter/i,okMaybeItsACandidate:/and|article|body|column|main|shadow/i,
positive:/article|body|content|entry|hentry|main|page|pagination|post|text|blog|story/i,negative:/combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget/i,extraneous:/print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|sign|single/i,divToPElements:/<(a|blockquote|dl|div|img|ol|p|pre|table|ul)/i,replaceBrs:/(<br[^>]*>[ \n\r\t]*){2,}/gi,replaceFonts:/<(\/?)font[^>]*>/gi,trim:/^\s+|\s+$/g,normalize:/\s{2,}/g,
killBreaks:/(<br\s*\/?>(\s|&nbsp;?)*){1,}/g,videos:/http:\/\/(www\.)?(youtube|vimeo)\.com/i,skipFootnoteLink:/^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$/i,nextLink:/(next|weiter|continue|>([^\|]|$)|\u00c2\u00bb([^\|]|$))/i,prevLink:/(prev|earl|old|new|<|\u00c2\u00ab)/i},init:function(a,b){readability.documentNode=a;readability.bodyNode=b;readability.removeScripts(readability.bodyNode);readability.parsedPages[window.location.href.replace(/\/$/,"")]=true;var c=readability.fetchMultiplePages?
readability.findNextPageLink(readability.documentNode):null;readability.prepDocument();var e=readability.documentNode.createElement("DIV"),g=readability.documentNode.createElement("DIV"),d=readability.getArticleTitle(),f=readability.grabArticle();if(!f)return readability.bodyNode.innerHTML;e.id="readOverlay";g.id="readInner";d.setAttribute("class","instapaper_title");readability.documentNode.dir=readability.getSuggestedDirection(d.innerHTML);g.appendChild(d);g.appendChild(f);e.appendChild(g);readability.bodyNode.innerHTML=
"";readability.bodyNode.id="readability-content";readability.bodyNode.appendChild(e);readability.bodyNode.removeAttribute("style");c&&readability.appendNextPage(c);return readability.bodyNode.innerHTML},getSuggestedDirection:function(a){function b(c){c=a.match(RegExp(c,"g"));return c!==null?c.length:0}a=a.replace(/@\w+/,"");return function(){var c=b("[\\u05B0-\\u05F4\\uFB1D-\\uFBF4]"),e=b("[\\u060C-\\u06FE\\uFB50-\\uFEFC]");return(c+e)*100/a.length>20}()?"rtl":"ltr"},getArticleTitle:function(){var a=
"",b="";try{a=b=readability.documentNode.title;if(typeof a!=="string")a=b=readability.getInnerText(readability.bodyNode.getElementsByTagName("title")[0])}catch(c){}if(a.match(/ [\|\-] /)){a=b.replace(/(.*)[\|\-] .*/gi,"$1");if(a.split(" ").length<3)a=b.replace(/[^\|\-]*[\|\-](.*)/gi,"$1")}else if(a.indexOf(": ")!==-1){a=b.replace(/.*:(.*)/gi,"$1");if(a.split(" ").length<3)a=b.replace(/[^:]*[:](.*)/gi,"$1")}else if(a.length>150||a.length<15){var e=readability.bodyNode.getElementsByTagName("h1");if(e.length===
1)a=readability.getInnerText(e[0])}a=a.replace(readability.regexps.trim,"");if(a.split(" ").length<=4)a=b;b=readability.documentNode.createElement("H1");b.innerHTML=a;return b},prepDocument:function(){readability.bodyNode.id="readabilityBody";readability.bodyNode.innerHTML=readability.bodyNode.innerHTML.replace(readability.regexps.replaceBrs,"</p><p>").replace(readability.regexps.replaceFonts,"<$1span>")},prepArticle:function(a){readability.cleanStyles(a);readability.killBreaks(a);readability.cleanConditionally(a,
"form");readability.clean(a,"object");readability.clean(a,"h1");a.getElementsByTagName("h2").length===1&&readability.clean(a,"h2");readability.clean(a,"iframe");readability.cleanHeaders(a);readability.cleanConditionally(a,"table");readability.cleanConditionally(a,"ul");readability.cleanConditionally(a,"div");for(var b=a.getElementsByTagName("p"),c=b.length-1;c>=0;c-=1){var e=b[c].getElementsByTagName("img").length,g=b[c].getElementsByTagName("embed").length,d=b[c].getElementsByTagName("object").length;
e===0&&g===0&&d===0&&readability.getInnerText(b[c],false)===""&&b[c].parentNode.removeChild(b[c])}try{a.innerHTML=a.innerHTML.replace(/<br[^>]*>\s*<p/gi,"<p")}catch(f){}},initializeNode:function(a){a.readability={contentScore:0};switch(a.tagName){case "DIV":a.readability.contentScore+=5;break;case "PRE":case "TD":case "BLOCKQUOTE":a.readability.contentScore+=3;break;case "ADDRESS":case "OL":case "UL":case "DL":case "DD":case "DT":case "LI":case "FORM":a.readability.contentScore-=3;break;case "H1":case "H2":case "H3":case "H4":case "H5":case "H6":case "TH":a.readability.contentScore-=
5}a.readability.contentScore+=readability.getClassWeight(a)},grabArticle:function(a){var b=readability.flagIsActive(readability.FLAG_STRIP_UNLIKELYS),c=a!==null?true:false;a=a?a:readability.bodyNode;for(var e=a.innerHTML,g=a.getElementsByTagName("*"),d=null,f=[],i=0;d=g[i];i+=1){if(b){var h=d.className+d.id;if(h.search(readability.regexps.unlikelyCandidates)!==-1&&h.search(readability.regexps.okMaybeItsACandidate)===-1&&d.tagName!=="BODY"){d.parentNode.removeChild(d);i-=1;continue}}if(d.tagName===
"P"||d.tagName==="TD"||d.tagName==="PRE")f[f.length]=d;if(d.tagName==="DIV")if(d.innerHTML.search(readability.regexps.divToPElements)===-1){h=readability.documentNode.createElement("p");try{h.innerHTML=d.innerHTML;d.parentNode.replaceChild(h,d);i-=1;f[f.length]=d}catch(m){}}else{h=0;for(var j=d.childNodes.length;h<j;h+=1){var k=d.childNodes[h];if(k.nodeType===3){var l=readability.documentNode.createElement("p");l.innerHTML=k.nodeValue;l.style.display="inline";l.className="readability-styled";k.parentNode.replaceChild(l,
k)}}}}b=[];for(g=0;g<f.length;g+=1){i=(d=f[g].parentNode)?d.parentNode:null;h=readability.getInnerText(f[g]);if(!(!d||typeof d.tagName==="undefined"))if(!(h.length<25)){if(typeof d.readability==="undefined"){readability.initializeNode(d);b.push(d)}if(i&&typeof i.readability==="undefined"&&typeof i.tagName!=="undefined"){readability.initializeNode(i);b.push(i)}j=0;j+=1;j+=h.split(",").length;j+=Math.min(Math.floor(h.length/100),3);d.readability.contentScore+=j;if(i)i.readability.contentScore+=j/2}}f=
null;g=0;for(d=b.length;g<d;g+=1){b[g].readability.contentScore*=1-readability.getLinkDensity(b[g]);if(!f||b[g].readability.contentScore>f.readability.contentScore)f=b[g]}if(f===null||f.tagName==="BODY"){f=readability.documentNode.createElement("DIV");f.innerHTML=a.innerHTML;a.innerHTML="";a.appendChild(f);readability.initializeNode(f)}b=readability.documentNode.createElement("DIV");if(c)b.id="readability-content";c=Math.max(10,f.readability.contentScore*0.2);g=f.parentNode.childNodes;d=0;for(i=g.length;d<
i;d+=1){h=g[d];j=false;if(h){if(h===f)j=true;k=0;if(h.className===f.className&&f.className!=="")k+=f.readability.contentScore*0.2;if(typeof h.readability!=="undefined"&&h.readability.contentScore+k>=c)j=true;if(h.nodeName==="P"){k=readability.getLinkDensity(h);l=readability.getInnerText(h);var n=l.length;if(n>80&&k<0.25)j=true;else if(n<80&&k===0&&l.search(/\.( |$)/)!==-1)j=true}if(j){j=null;if(h.nodeName!=="DIV"&&h.nodeName!=="P"){j=readability.documentNode.createElement("DIV");try{j.id=h.id;j.innerHTML=
h.innerHTML}catch(o){j=h;d-=1;i-=1}}else{j=h;d-=1;i-=1}j.className="";b.appendChild(j)}}}readability.prepArticle(b);if(readability.curPageNum===1){b.innerHTML='<div id="readability-page-1" class="page">'+b.innerHTML+"</div>";readability.pageBodies[1]=b.firstChild}if(readability.getInnerText(b,false).length<250){a.innerHTML=e;if(readability.flagIsActive(readability.FLAG_STRIP_UNLIKELYS)){readability.removeFlag(readability.FLAG_STRIP_UNLIKELYS);return readability.grabArticle(a)}else if(readability.flagIsActive(readability.FLAG_WEIGHT_CLASSES)){readability.removeFlag(readability.FLAG_WEIGHT_CLASSES);
return readability.grabArticle(a)}else if(readability.flagIsActive(readability.FLAG_CLEAN_CONDITIONALLY)){readability.removeFlag(readability.FLAG_CLEAN_CONDITIONALLY);return readability.grabArticle(a)}else return null}return b},removeScripts:function(a){a=a.getElementsByTagName("script");for(var b=a.length-1;b>=0;b-=1)if(typeof a[b].src==="undefined"||a[b].src.indexOf("readability")===-1&&a[b].src.indexOf("typekit")===-1){a[b].nodeValue="";a[b].removeAttribute("src");a[b].parentNode&&a[b].parentNode.removeChild(a[b])}},
getInnerText:function(a,b){var c="";if(typeof a.textContent==="undefined"&&typeof a.innerText==="undefined")return"";b=typeof b==="undefined"?true:b;c=navigator.appName==="Microsoft Internet Explorer"?a.innerText.replace(readability.regexps.trim,""):a.textContent.replace(readability.regexps.trim,"");return b?c.replace(readability.regexps.normalize," "):c},getCharCount:function(a,b){b=b||",";return readability.getInnerText(a).split(b).length-1},cleanStyles:function(a){a=a||document;var b=a.firstChild;
if(a)for(typeof a.removeAttribute==="function"&&a.className!=="readability-styled"&&a.removeAttribute("style");b!==null;){if(b.nodeType===1){b.className!=="readability-styled"&&b.removeAttribute("style");readability.cleanStyles(b)}b=b.nextSibling}},getLinkDensity:function(a){var b=a.getElementsByTagName("a");a=readability.getInnerText(a).length;for(var c=0,e=0,g=b.length;e<g;e+=1)c+=readability.getInnerText(b[e]).length;return c/a},findBaseUrl:function(){for(var a=window.location.pathname.split("?")[0].split("/").reverse(),
b=[],c="",e=0,g=a.length;e<g;e+=1){var d=a[e];if(d.indexOf(".")!==-1){c=d.split(".")[1];c.match(/[^a-zA-Z]/)||(d=d.split(".")[0])}if(d.indexOf(",00")!==-1)d=d.replace(",00","");if(d.match(/((_|-)?p[a-z]*|(_|-))[0-9]{1,2}$/i)&&(e===1||e===0))d=d.replace(/((_|-)?p[a-z]*|(_|-))[0-9]{1,2}$/i,"");c=false;if(e<2&&d.match(/^\d{1,2}$/))c=true;if(e===0&&d.toLowerCase()==="index")c=true;if(e<2&&d.length<3&&!a[0].match(/[a-z]/i))c=true;c||b.push(d)}return window.location.protocol+"//"+window.location.host+b.reverse().join("/")},
findNextPageLink:function(a){var b={};a=a.getElementsByTagName("a");for(var c=readability.findBaseUrl(),e=0,g=a.length;e<g;e+=1){var d=a[e],f=a[e].href.replace(/#.*$/,"").replace(/\/$/,"");if(!(f===""||f===c||f===window.location.href||f in readability.parsedPages))if(window.location.host===f.split(/\/+/g)[1]){var i=readability.getInnerText(d);if(!(i.match(readability.regexps.extraneous)||i.length>25))if(f.replace(c,"").match(/\d/)){if(f in b)b[f].linkText+=" | "+i;else b[f]={score:0,linkText:i,href:f};
var h=b[f];if(f.indexOf(c)!==0)h.score-=25;var m=i+" "+d.className+" "+d.id;if(m.match(readability.regexps.nextLink))h.score+=50;if(m.match(/pag(e|ing|inat)/i))h.score+=25;if(m.match(/(first|last)/i))h.linkText.match(readability.regexps.nextLink)||(h.score-=65);if(m.match(readability.regexps.negative)||m.match(readability.regexps.extraneous))h.score-=50;if(m.match(readability.regexps.prevLink))h.score-=200;d=d.parentNode;for(var j=m=false;d;){var k=d.className+" "+d.id;if(!m&&k&&k.match(/pag(e|ing|inat)/i)){m=
true;h.score+=25}if(!j&&k&&k.match(readability.regexps.negative))if(!k.match(readability.regexps.positive)){h.score-=25;j=true}d=d.parentNode}if(f.match(/p(a|g|ag)?(e|ing|ination)?(=|\/)[0-9]{1,2}/i)||f.match(/(page|paging)/i))h.score+=25;if(f.match(readability.regexps.extraneous))h.score-=15;if(f=parseInt(i,10))if(f===1)h.score-=10;else h.score+=Math.max(0,10-f)}}}a=null;for(var l in b)if(b.hasOwnProperty(l))if(b[l].score>=50&&(!a||a.score<b[l].score))a=b[l];if(a){b=a.href.replace(/\/$/,"");readability.parsedPages[b]=
true;return b}else return null},xhr:function(){if(typeof XMLHttpRequest!=="undefined"&&(window.location.protocol!=="file:"||!window.ActiveXObject))return new XMLHttpRequest;else{try{return new ActiveXObject("Msxml2.XMLHTTP.6.0")}catch(a){}try{return new ActiveXObject("Msxml2.XMLHTTP.3.0")}catch(b){}try{return new ActiveXObject("Msxml2.XMLHTTP")}catch(c){}}return false},successfulRequest:function(a){return a.status>=200&&a.status<300||a.status===304||a.status===0&&a.responseText},ajax:function(a,b){var c=
readability.xhr();if(typeof b==="undefined")b={};c.onreadystatechange=function(){if(c.readyState===4)if(readability.successfulRequest(c))b.success&&b.success(c);else b.error&&b.error(c)};c.open("get",a,true);c.setRequestHeader("Accept","text/html");try{c.send(b.postBody)}catch(e){b.error&&b.error()}return c},curPageNum:1,appendNextPage:function(a){readability.curPageNum+=1;var b=readability.documentNode.createElement("DIV");b.id="readability-page-"+readability.curPageNum;readability.pageBodies[readability.curPageNum]=
b;b.className="page";readability.bodyNode.appendChild(b);if(readability.curPageNum>readability.maxPages)b.innerHTML+="<div style='text-align: center'><a href='"+a+"'>View Next Page</a></div>";else{readability.ajaxIsRunning=true;(function(c,e){readability.ajax(c,{error:function(){readability.ajaxIsRunning=false},success:function(g){var d=g.getResponseHeader("ETag");if(d)if(d in readability.pageETags){b.style.display="none";return}else readability.pageETags[d]=1;d=readability.documentNode.createElement("DIV");
g=g.responseText.replace(/\n/g,"\uffff").replace(/<script.*?>.*?<\/script>/gi,"");g=g.replace(/\n/g,"\uffff").replace(/<script.*?>.*?<\/script>/gi,"");g=g.replace(/\uffff/g,"\n").replace(/<(\/?)noscript/gi,"<$1div");g=g.replace(readability.regexps.replaceBrs,"</p><p>");g=g.replace(readability.regexps.replaceFonts,"<$1span>");d.innerHTML=g;readability.flags=7;g=readability.findNextPageLink(d);if(d=readability.grabArticle(d)){var f=d.getElementsByTagName("P").length?d.getElementsByTagName("P")[0]:null;
if(f&&f.innerHTML.length>100)for(var i=1;i<=readability.curPageNum;i+=1){var h=readability.pageBodies[i];if(h&&h.innerHTML.indexOf(f.innerHTML)!==-1){b.style.display="none";readability.parsedPages[c]=true;readability.ajaxIsRunning=false;return}}e.innerHTML+=d.innerHTML;if(g)readability.appendNextPage(g);else readability.ajaxIsRunning=false}else readability.ajaxIsRunning=false}})})(a,b)}},getClassWeight:function(a){if(!readability.flagIsActive(readability.FLAG_WEIGHT_CLASSES))return 0;var b=0;if(typeof a.className===
"string"&&a.className!==""){if(a.className.search(readability.regexps.negative)!==-1)b-=25;if(a.className.search(readability.regexps.positive)!==-1)b+=25}if(typeof a.id==="string"&&a.id!==""){if(a.id.search(readability.regexps.negative)!==-1)b-=25;if(a.id.search(readability.regexps.positive)!==-1)b+=25}return b},nodeIsVisible:function(a){return(a.offsetWidth!==0||a.offsetHeight!==0)&&a.style.display.toLowerCase()!=="none"},killBreaks:function(a){try{a.innerHTML=a.innerHTML.replace(readability.regexps.killBreaks,
"<br />")}catch(b){}},clean:function(a,b){for(var c=a.getElementsByTagName(b),e=b==="object"||b==="embed",g=c.length-1;g>=0;g-=1){if(e){for(var d="",f=0,i=c[g].attributes.length;f<i;f+=1)d+=c[g].attributes[f].value+"|";if(d.search(readability.regexps.videos)!==-1)continue;if(c[g].innerHTML.search(readability.regexps.videos)!==-1)continue}c[g].parentNode.removeChild(c[g])}},cleanConditionally:function(a,b){if(readability.flagIsActive(readability.FLAG_CLEAN_CONDITIONALLY))for(var c=a.getElementsByTagName(b),
e=c.length-1;e>=0;e-=1){var g=readability.getClassWeight(c[e]);if(g+(typeof c[e].readability!=="undefined"?c[e].readability.contentScore:0)<0)c[e].parentNode.removeChild(c[e]);else if(readability.getCharCount(c[e],",")<10){for(var d=c[e].getElementsByTagName("p").length,f=c[e].getElementsByTagName("img").length,i=c[e].getElementsByTagName("li").length-100,h=c[e].getElementsByTagName("input").length,m=0,j=c[e].getElementsByTagName("embed"),k=0,l=j.length;k<l;k+=1)if(j[k].src.search(readability.regexps.videos)===
-1)m+=1;j=readability.getLinkDensity(c[e]);k=readability.getInnerText(c[e]).length;l=false;if(f>d)l=true;else if(i>d&&b!=="ul"&&b!=="ol")l=true;else if(h>Math.floor(d/3))l=true;else if(k<25&&(f===0||f>2))l=true;else if(g<25&&j>0.2)l=true;else if(g>=25&&j>0.5)l=true;else if(m===1&&k<75||m>1)l=true;l&&c[e].parentNode.removeChild(c[e])}}},cleanHeaders:function(a){for(var b=1;b<3;b+=1)for(var c=a.getElementsByTagName("h"+b),e=c.length-1;e>=0;e-=1)if(readability.getClassWeight(c[e])<0||readability.getLinkDensity(c[e])>
0.33)c[e].parentNode.removeChild(c[e])},htmlspecialchars:function(a){if(typeof a==="string"){a=a.replace(/&/g,"&amp;");a=a.replace(/"/g,"&quot;");a=a.replace(/'/g,"&#039;");a=a.replace(/</g,"&lt;");a=a.replace(/>/g,"&gt;")}return a},flagIsActive:function(a){return(readability.flags&a)>0},addFlag:function(a){readability.flags|=a},removeFlag:function(a){readability.flags&=~a}};
function ipPollReadabilityAjaxDone(){readability.ajaxIsRunning?setTimeout(ipPollReadabilityAjaxDone,250):ipReadabilityCompleted(readability.bodyNode)};
    }catch(e){ _greaderipb414353 = true; }
}

if (_greaderipb414353) _ipSendipb414353(href, title);
else {
        readability.fetchMultiplePages = false;
        readability.init(document, document.body.cloneNode(true));
    ipPollReadabilityAjaxDone();
}

}_rlipb414353();void(0)
function _clipb414353_close() 
{ 
    var f = document.getElementById('ipb414353');
    f.style.display = 'none'; 
    f.parentNode.removeChild(f);
}