import base64
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import time

encoded = r"""
{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;gA1YMqL0foGe^$F&jkXXKfZTm(UKHa?`NPfNf&+(Zw>rdy|NqMWYivpTPqKg}0u)C-Lz^
S}+Vmkdzb|T(hUwHE2nR#gdKzsxQwRps9;xae(I)84tFp$Rc5U@+KLX-+$Gd3Faa><`Fw0esNDS7=2E$`zHH8w-TNZ3VA-bEpDDV
Kc!c7CL7~nif|O$8KU@mmqp%PawzVes3zln)6d%3Y2K7vNG?9z226(ZebI^x*{cX;rjl0+b##XwOrP+ihf*x0q(u>+#CBRHV+~D~
4=(G@5ksqQ373)4OR<1t@}<*5MTz?}9;Kd<QQtm*dEm^TVK&S9V-NnyQFhw)TL<VoL=*g+iR#W*pg?qi<vM8+VuVj+ZP?7hYI+)y
&QMONei0cf{8msP=u&TJdN2jL-lrirjE_hw??})-XQR^{1X9aL(YeX|{cqB&X0mXr@th@C1D(lI#_Hf0b%$b<QSSYqGW_~XHPEaA
S&57+a~H}^==Do7SFvIxSr%Px36lJ?rqqz6%_ESKV#{2(90~EgV8d`9EDD2@%;s`_Qd*QqVV#8WS~C^Oa0X3LCbtmeaM0wXoCnB@
YW2!zJbTB#5F!S^$iyx02hER@Fej-qz5VeW#>`{;Rf<(8KL>sojbGazQ=sx=aD;Hq-UwxsM5U<c9JDw5x&r5m6$fcbT727fNg|`^
av2U_*S6QID1}h2SzlkRid_?h_u@$@$X^E3Q>BLf9>8a`8q@PF{W2SmH(y>LU;yoiz@SmKt<R_2O@BeS1ca_G&&Msb4rz=>ymUwy
5n24)JZPa~%IS(ec2#JMeWx*Ozjg|JBA6XmlHnvQij&2HYYfDWe~>;rH~s&Enm*b+L6KZYFNy)|2slI-{Qpefj;NR!pb2f2<}ct5
VXSEcGo~IR^(V`MS~o5hbaD!6m^At(Z4SkwGLEpXQ=OZ(@So_IT=f)VJ+OIRn58&6TO|(uyIJvdTbmBw<S$ToU4*thG7T8wmC|;@
pIlH*p54}@W3+g1tS$0JTyq#SFs9(N(K9=IlB2hc;J+1xr^sGxtZ3#VU`%<B=leysjiM$JZ?C-1sVjf<FbLPitqj^htD;=A--<)#
w^)~L$=O_<PNpSg`|5}%s47cOOSuzN%Jx7TczvOmEjRnlrsbNT6j*=}!5Gh+E4-c~oVI7;2&$jkgL+3edEgxt7iT!vM$wa9XORx|
O-v$^y|A8Ge4PrrO6y(3&<e8<*!M<9ZB52{Zr7?81g_MhOrK`_`Fi~JdDbXk;OyPJ(y&7O+#uGPd{YVSzxKf^qounLFIJ*^psqm&
a8k+J*-P3Klcf&%#ihVY3vALjnsGRp@p3x2=|U<6&HiDb_4Z2Qr$Nwa>kk_ikZI>Dc-A#{A7F9>#kRppZa%fJ=EqL2lpVHg`A-9(
)Mv(`P)}n_&~JYOzNXufXKQNz=@*HB0^9h$Qo?URu1e~XpYqP2Qv?)CD-+IIQBWm2(Y1mb{|08GmWEYhd(lz^w{#0<Fm&Zm6qTBa
mVY4K=2yo{=Kc}>rog2qj0jyhnQ*;PG+KNDi@_~G^(nVTq=_w|`ebzb6oT`2a_~6Q@|zRCGsE)#hE|dbp%~{lrpR&(#swueK086O
-*>M8iCD>$XO)E)A<H!v85FS~``x*`ZVi0mr2~oBo~GNr1BN#`bg8I-;}>AwcOf})tMKxnGXV0V>H)2v7*5JTTrX}bX!_AD{*rD`
lY79yvhab7qIVWPk3SexR8Z3c2q!jAOk*<Nspa%#0DcJZ5uki-shZnu?t7qBrlCD6Za3|_=`5Eg+xn{ARb@T1aoUuWTx$=&PBn5*
>SB#pah8F?u^9W>M9H{KG*jFf5oN+n+Ajv^U6d?h_nP>gnwDUy_FiW`e=OSJ_tH>6<BTtT&!BZvo;KE|DKzXdbZJj?JgJx_M!rap
`d=b3yosPt1$a4rb@e-9kjtkQ2a^+C8A3U^pQZONY0r_ZY67D+dj`xlYKwF#pjLVL22_o9jxMd_@!{CoK@C58iu-^Rk>^7aY8XGm
<|Hgg0Af(o0F;WA)Q!lrlIiVd!;Y(cfN%M?gR@r$aLV=m3MurTMrr!4BjmcI-JiEoPj!2<?wMOIaOL@#i(<yvA?;pIGk*oV&PQOK
4T-zpTGP2^rN*JN1kCLpp4IPZunqsPsLCR4gYU81*N)`4Lj$mt)snkuFG%as%grvSxjIl4)n{qM0V(vb9DetztiwMgN+EOgI<Ga7
)h!+WE5MZR7ufNPFN+M#c0!2xmU`y&%pZuUbcv;+icrq!b@;O|$UuRuOd1vL^p_yal+HmHgFv_vA^#oVc~pVqAKU_k#OYskcHKyB
CYsx<q3q!x4j@}53g|-JRHzWJ<7@N+;_zvOg;@z8WpX&;1QWq2CG6gKI!nOJD_q~rAq%3Ejv^CvN7CrnE_w_ervVM3T*OiK@C>3!
%MvARGQq%003K~scW>3bKhd%@hNJyHe?ru_KRb4@Lq-ZVe>o(C--GG>ztYM`uPw?ZFN6K0SEq%NZz(7E@)heW9AHSt-`6UdZQu(y
KNuR{n~a_FK;<{VB~D-QHPpk93{HzlMKPZ&cIxvSiqciu9UGCeAt?#5?Kzs(Wh1ivimn_Eh@wF{Hyok-8DIhrOoXvap9LUU-7ig>
`mh+D0UWr;OsEV_`W`j^i84lIImcF867X78_P&Y+<&oJfN)^x6?(EGFt-YwrH2%T_d(h^~>(p=hE=yDA&GL%OFnOt{e8R8R?c<n7
q6pxUmWtf>!#S){eR|WI92UTbUg0F??6~hXSFylRK;hq_F<{;Ht=mMo@|MDp#iu!8PAqCO$>}YIfz0C&w`a;ELL5q$zQn-@vcIGu
gq9@j@2V-zqC>QsP6WQ^#mi0gB>M}kpBKSIbAjAl90i<5^%sW66!;A(N|t9PL`ofUU6O(}ei2y`l(fiF6yoF2=D2A<yL=!`<fP&u
Ur80?q{Oxuud6=!v&X&2Jb234$ZA*7D@=cW(SWw3z#YG)Df2ZKp?CWR{{Yw|6NPr*p;e~`)uy{n@Y+l#=_X|mzl$8)Yk#=}Sds_6
_E#@0R5dSq7o1EXwdI3zlOj>Jfl2A!V%)3;WB3uyAdk{cMc>D(|L&rOw1U`KvLqlW0KSVfPiq16<-7Am$o(byGM|nG_EwTh583Ez
yAaH{`<m0<f8+!|zfsxcSQak(YxpCVGVZIneH?T}G0aA5(KoM`Ivx1Y_fnKAhTo<AFgqsv(FjX8rByLPAN$+RcMa%US|g+Kthl9G
DL=+KNn8n2XN;|s173+>8ZSbky#UxaFnrv?>7dhh%v@*j8VgZZVW~#MBXoNrQo^9+kL-8LMQl?j7Dau@Ef47fpH%*T<x~IH+SlpM
_#rmhj?2+PQ3N)Qt8zXA{koNcY_wZv<|oRG<@V|~DvW#+7>XniI8PxU-BwC@`9B;LrAS1uAN+3V`isw#O2Buz4zT1v%+#fTBJJdV
+XvaK%A0>m(iQ1iKH}nU%}1Sn^ob0y9%7D{oho2alysOLHKAR6oncGttd>_W>rVuhZx_zXf%P0BE$**H5^7|kx&(Y;n(T^8xhzHx
U<??YJL&xA#BMPY>3m_Z%UkZ7tpGXUPbJ(yj|u}5PmyUlpZon%m5Z-1)ZIwTyzEG1er4`S57^R&))0^^LF)Q~O4WG+@SEGfH+X;~
z8=XO;O?Y|L1_<_sH*>j+8b;A%5kc8z)WfaMQROQbE-b)^r5!y+iu_tgL<O$t-DN7@deIm-Ln#G2^d#E>ttCz$70oUYRt`|b!?-j
O3!Q!82^Pv09axm59YF|R^JOHF#-7F%x>O_Bv$X&vx&iMzvca@lul)~X5+h%inB;4LjTIy;8IO<>|2g2EQ<BKNS=q*-%c}^xs;$B
@QI~kurd`IV#$1PSCNc8pf!i|ao7bco*NAuE@EuldIcwko+&f1EttxbY-W$elK>8Ts?#s~DxG4@%vx3M+`t_ASEd!^4)%M5i*6?-
Q1>K<OUM1l3YSz9Ptv#`4!05y07vzjdv2#C#|@~#$RDXtiS9LRg{Q4>IHY~ig)vM^5fo5*-R^@o!Vix(w@VR|<RX`tO|Sl<?e*7Y
Sy5!TTPkhSd{>wyB;X$t4cd?vHnxlFRJMYuuoOy0bHL~KeH#B0W2VY^P3Rb!J6VA37`~z1n-gtN?yZ2^b``DC2=By)z)X2WO{noW
I3E>;#e*(gvkb45W(}M6-b?JNz7iT8ZiFxI2nFmamI2&lYHgBTG?dT8WgTt+iISd6>z-IX#L3Y=fs>P@nm2ab+#UVhhtj|k+0zl^
ogfR|V>YF8sB>%|X82&G(hWYe3pB5E2l;U{Zf0;;6!3l8Gn8`DkGqA8IAQAoTONe7*cGA&A8v-*S_={9b+C4Ly-|8JZ^y@!s?twU
$jMdB8+MERuNj^w6T;vR<4F1Eg-a0p6#eka>AnuU(C6k~wYLXK{e*aivbq!dhEQtWlVuKKYiV1SDvCa6zI1Nz_MHgn&-6b&F%n#+
=j3c<Zy@ac52}GTH)AjlXO9@2-2|$pNt8~)6P$P?tp^_2n^-KS2vtcxMc}{doA?1G_zZX)FFre#TY4^84N+Y(%e8KSQf3^tZKR;p
7gVB2(aS+|8;Olssiu>;lh~~$_Z-u1Y)Ui0yKGju&d_yXg=HEt$X`iy375?S46i4vXLfSDqY?=rf*Rx`t~^KiS=SN)?C$WblEFZR
Sx7Z}`67yYJq|%onm1*($1ilz#~k9l-JXa@HXE>kqW<NmF|67BtjoiH$^s)`dRi&z$&JXgoBu2l^<CS}kKQNL2E7}4NG|da<*A+r
rAPX9Q27?X{Fc+W%jD>#p^%}g;baB}DU8YnmIc#U6}4uRT)Jiub%j_CwO7sdpQ6!{fsGEffdcC()$odCRZUu6A+u4F@FQ`^&?vRH
UE(ngLe3E&G1SO&hXnMwgGR2X`)Z2|8-I%G4=4CyNOIYJ9G@qsDLq|NWIvnQm_EqlcD|@DJguDXrc8+1U$-glS1lzp(~RRsYu`a|
&@gL8zR<M0$M^YI@)Em_HzsV6U?3;(EKP#dX#Yf?c$pjyYoapqo$r7&>aRuRG^tknf1Rk`@8*#TZd`<z*~Z7f=qM-HP<DOZ9`=bv
I7<bxv?JAlP;^S!a3FqRU5lQ=6y%<8L8f9@*Gqarr@w6b%Ir@#Q-c2$RvQjU9%rqf6hVSp56a@EPrLnl%r7H!ZZwGEZIvU%hfZX}
Lq>iLN!pG%D3IVCwHellcg0p<b!f*s4FX|xpiUA}wR9gvl=Cj8-dTb}!UNLX1y`(jW875Ud(hgevmM%_(^TC+MM@drDv8Yq8b%^&
%sFW-z{qmpNNv8%GPyF7z8?`4x4i>~d8OZ@+}q3w=}(D-bq(y_E$B-B9iibOCVu~lGpI0hDAmE$(1hTWva68daR<+sk(w?wF)HUj
C2O$(0kapkcSj=Kd;1)@fUKZSi&7j2Ai;+KOVHn|+otV}(>^kK4ap0|*C=kdZim2qhAgE<3%d-D?2gVf^2z#-jlNo-aMPhOF<yI4
<qJ#(1`Ii&zxsc`kyS^+YTW&YbnI(U9(r*tpBWQBCq-oe=l#No@nJM^zX()6x*lAzX(M+JrZjR><7@tGI(HDdw0TMw)Dd@tiGH|I
1*3)l*cRUr*%}9ToN@0ywN1^4_xG?Zl`rqDQ4uG_Edf(&J6v89Bv^l-$7+QTcqM{jR4{q|p7tlY85Zg|C)C2v{+wx(^$!`_m78wy
;33_Yb+)=P9^0)-XRkXoj!-<ScU-<WLsl-!^eHD++%1qQ4=f-EZJCGn4$;G8@g<bj^O@;S8>PMiYI8ot4u2w6g~wDmZw|J}#hE6n
4cW1i=7TgLK7`4GMXg5>@h?Ts4?jwI&^SoMHC;gF)}2?~V|;wfe>YvwU1IOSs}1VA1Fr$wj}d%~eUP`NHI1r+q-iW=s8IC+aX6Uj
TSwi<y{1v1$+ppGt0}`z?vWe2X|+qeKC7Qy>bGLK{Fc+n-A-eY`=MR!=B;{4#2dl|Ly*AVj_?&B8B}_S3EzGA6GB`MvOiat<RTU6
u%X)>#ZdQEhKnL<w2qto-v^1oDqU(MO$3DqD~IG4#1e5(p)>(xmOFRzuu1eDe{JIn3~?;aZWI1d;RPc^z_P;KWbzv!&||o=s)mlm
11&ZZoLTx`$Yt?BL36^6uXVKwoWD-j?C%NcjOb2hUnsq`9E3Q`u5{wYEKcXkjx#0>tkeW<0JC~P6>N|b>fJpe`E(e+<y!Unp;`!<
$(pA|iN1fz!g;z8!wByq5Gu1+m#kD=wdw?NQq>5a7sFZjSc^){P<AM-gCsXAw_)}9uvmOTBuLv+r+13h#uM@DwU{8rB+Vpiu3vg)
wvDN}=}pJ!Di2)Kb|Kl%$DA5TV!c&E$ASM*6{4`DD;~+I#SdjPU3tp4`B9cU*AFiw#BUU~LR}oN=|APir&wf@L%{bwGGofN@wQen
35q<epYz2w&ZUDm1%)OvO}(T)0>e9#9R)4^V|oNMDLn9H{M0~qX!BE+EMGtKaA=9Y36T~6UQlvnYw^W+L2Tb^Bd47<5F4H=&{t}?
82HA!&Wp0L4hP6Up&|v0fhC@9rzTg9YU&#r4n@d9E_@*Y4AA?XL*()A9Hn~$W1$s5deJ#%F+*F@fHe1A3Ai<=Z`QKlD4BYR-9}L6
5<Ba_z7)6KtgVIhHPM&Qfs~3$-tTO$J)KC~S8h)`Dn>LLwV0np>qU$(>I3S?d}VUOXnzuVfzkNd?S2V2ldgzzFM&#}_|*97TWAPN
b36u7HRfDOZ@|91L##}~EYk1t@AH?FM`JwGDp!wrbAEzHwWP8?PGyDfO`sB@qvPnGCvE^QZ_=LsKK0tlRmBN*YX_aRGCi5^!~)kt
|EvML{>*&C;bO<Nzr82`Uq&+=P!NYzvAUCjqK9g*MyZd?fgeG53?4X7F&I6Dgh?1bD6*i7l}4QbnV_Aeu;G>HV@CD&${2uJ3;?{{
i@+C^N=xGJdT?DV)fA5jc!Px*jFWZ3f)lLWoNlGN{)B>PWf?fudjnd6U9+2+{@3+Wj}{uMxT~;pe68RNxn3NA|HD!&V|7gA^X(r;
L!p(p82ZgnuFPLpyy{z6)z%e42_+aLa=@upL4mLE2j1{yAs0&bPa}k^y^|#}h@kBmDVmRdd0(%KI_PHMs(VQ>l?s!CitnMvXQ+3D
+f8Kb?vYF9iP;=DhQZahg6Zr2Z3ojJt7bjJ!~N6f1VRHzNSnNzSD<i<;KbVW`E%14#;u{{Yb;c&o+(+Zb6MC#itWT)nMF{b5$FT#
`tsQj8m<P3*>F$tM%iKU=5=h0`Ks$#M!-12HrevzYJ_2HGw%Z_F1ZJX!X*Pk#KQ^{LUe`7Cb^VNz9-{hrR=2mQ5ErI3bFB>Y;TaX
7m@pA!sy4R7zFh<qibGz|DV+#T48|DcWuPqDz=TZ&^8??U~l=a3l1UI+sb)Z$Gzy_M~Gk|ET#@IJNhp5OlO($G4O;b&DACQKJr0_
3RgKIbn1E+G9;~FS6zXJLhLix<^|z&f4f9&O(7@HK6XbLNIti(B}hJ}y+^12dNA^~EWME$0c<w)q!r3ck+~7d4^1xCr-YY~@1W~?
nk|&52GYNUe-=Eyb}hp@+$xkaX<b%R&8Uv6jm)S0u`|*$`L!)lZ2y+E{*I36>tdV3(k9*C2-eJiXR7Y_dO5$fFedf$Qc_7NEQ7%g
E?APJy~O>7;R}(0w*sEXCTNIWX~xGf&jD;kwHw*==d=K$t+s#dj{<Z!MKCv@ojyKV?A<JyrhN8immL-29>eJn0B6PCZep#{GZW+G
ShMADeHiAcq-x>JJz<HN?4h=aT<K3d(&WvP(U2f`sL7k@?>~GiCK;2}`1Dn-i_?iRTpEVR9O9B5-*NSDO#;XyLeJFf9znp4IMn}m
Z*Y4DUi_bqAKI*8{xU_uX>Lv$%3(i$j6as%0pIeZ;9PM86qb};MBqF{d1+u{wDK3838!BX`W4T`{P2~YPaPBgG@731&~0{7Yl%a^
7MX*pd*zU1r<YoWpV>e=P&Vie5Qx+Nl`^EXIrrTBJAgRy{480Qm3M9e24xte;KQ;1*;{CM1eB#v-NS89ovQ$05qEGXj4}q!4X`b}
+Zz)Ney_M9-X*#6{^aP<n0pPOM{VY9K>)|0%P|h$JoF4Y2Aqsa|IGD*(03(~6mt@zAxv}0F2T~^9KpjW){?LfK9eMk51-C)=4y&-
dm9Gd@x5L&yZGEh3$ZJ*Pv-Ga02!tm8oFoRmLLvOy`~GTYoz^%trBIL=wn+kFLH<&s)NaIZLzs;b$FOI@Jd%nhou10dT3Fd%FLYK
|K3-cvIHSt5`2A2(_gQKb|)kI+TuA<x}}XMnmx^FkkZI#$NKttE@w7-sEeV(Qzq|aJ~Igr2_len*?sYR6c_H%-S}-Et#X7~h9$v*
t-+Vvtpo8v3HIy}#&N768Y4C#(kFCdmj~40x#Gx>YW5<{N7qr33UgQbDfE>Y18Ro{DckRY7xWm>E8eT4{PYemjEplz!6YqpdJh6S
$R;EE1v9IQmb9e(iQC-8b=ZhJ{BN<>fIWs~;+q4HjEfS+;Md-eNae9wz9FI_RjoZ=vl7g)^9txsx(U(8Lf+WR8?7r8eHeOd`AvVy
tLOWlH`9B?%9~B{R$A~(E}?yPPrsy+BI$z>baqWH0|Bxn;1*xgVn@8W(`h=8+bUMx+S7J5<)WbK#fogOcQ^Ja;b|tf<pMaWa;fx-
gVJ~Hy<drQN{e{RdC@B`_#W-{a6xVeo4P5z-44IU0vJmt>*HAv`GC_RZ+*tv{liGq&l}yJkKl6VDT#BHp9c{h@x2~?pMong{#A=>
%suJO+1&C(WJ4vx*Y$4UJlWu_@NoQOhDtoUowLgW=QHronn3L=hsEpL60OpwwhjhI{sr~whg{Ev3GjzaLcs=+o$#p2^a$gYxiLoQ
>`n(@S<oi*5H&pLb%ZNciz8=BCuPXXoN}N)S)6GLjEPx8hhzTP^(c@5UBjs;Y)|-03RwVJ_Qv(Alfe&?%du+tdv^6)WcG-FXMktc
TU+2P_C^uN8$&-S+znCQ+xQv+_D9{{LwRK54(VBP-A81xFU&q)+NB&`E2zy9lyT!7rHn(XdMpZo<ZY_|yX;rWW*W@I(X5*Z!W@BM
qnsls0-Jr2VlNkLx1Wv~SK(9wm&IvD1A!;#at&)Jx-l^(Bb}@(F8=4A@u5iIDbO<PT|~x%FKum62{c;8sL)5A0px>_G-s=BYUDGf
mFwjN_yCQNdR_77Vcd+B+35dOtbF&7-n}{|F%_|=g6!M9NY;ONR(5$!ph*%7)USHd&?0HirF+KiYkvKT+jOcirUGA8c1PNak!buf
pF_C5xFyzSf^wG0jmSpIPgJ+FY}Tg9HlZ33PA%A*QDK_!z*-nVLGIJ0^VqQ)kuQ?_AwOFF6pEZ`fL=cTxp$KfXZU2sZ}HuJzy*+1
3MK})Qmsi_hC)@o1DIzG(T%~@?^jnbup8$kt0tz12X?{(+w%hL)%x+M+)5<%NcJTSl4xP8Mrc`{7XN!fS_`cJ=$dpNh#1It;_Uf&
(4GLyaBDcE?0TD__8siaz?@ecV^cAu=-@_pbXhYAO;Kn6Gac4^mM?oc(zX}VFg}NBc-Y|q?p=a5y4-M!r<oM`*!zlrq7i#j;na(D
4Q<siU(hxrlHpreufPrnp;CM+pLJTQ9P+RWFb&csz*maP?maiNU@8$zNb&^JiTqKs>SQG~7Evi!=F|(uz;2P1kWpfXc>RBY$XGYX
in*)^lDtSqAPid7E<Jjed#dXY_1lt^Kd22Nc$6Y91Cye2Os&*0b6Htw_;ccRkXl@n__i?>r(_VY9FjwxjW;P<v)}J+iQA|#H$?6M
>vZvK$qQhMQ8}wgZdC&4YJ($vL86<-h5-DU&ZmC^or{X`Y{iE)23}~gyW+b;%0u-som{1+?#v_&%#|$ZpxLdZE$hw2UQ6$V=PAj#
n!za*N?-H=!VlR}=GOv?ozI~O!52N)3x_9$x%N!>T%q!9K?9!|`@cOCts-R`j)9;t-+tK54lBe_Mu7z@qsr;qUq~d;9c%iH@RzU>
GNfKKzv?Bx^MmWMQhfmQnO3%DtqExEZ2>s4U-4JOOG1x)G1_j4^ohZqUsllC{E!-FAa<A_OlT3XUDd846-`<(l%dxU(UOX$p=I)u
1I#C}DcJ;k(`hRKlMSB{^-seiX?4sVeC#xw-qFFB5#4mF-qp+5hX{9w*-mL?bo+FjqiQZeG}zNfk<&n|=6Ed1vSqc0@)Zu3S+(!Y
ZK_Dhh!^~IkBrC=9uGaMsadP*xgTss+<oNTR7!%$f>P%M`NO_eY#JJ4BeQioC+tR;tWiHhwWeo39T^mB#`7HBa9=72sr#M<n0VhH
Bu9^=WSxL;suz=fY2xNy#RP{1=h&A@yH%^2)<|2%G54zF1{q*Z)4(|Gczbpi5ogaL?xPQpnEYVF*(SYyI^GkMZR>^s>MsV8-bCWQ
)(*;(KlQONh!M+}fd5V44#JFI<^|9AX0{)Z)~uq3dxM0K<6Y>nnP{ZE?fpXg(;jgsfm%}@#DV;iPD0ENIkO5Q7BnAuQ4WhnULO+L
!HOWqlLeQv(3^woXW>L1!jbKLoFWPR!F@H>NNk646(^ALY62<-9VB2<*kyxcx>CC+zsowzK78tLq`r#F`@18|52Ftc!F5-ijZYih
&hvepY#yzj-z9r&ci!6k4DkYVo+Cfg`{jqZB!29a%v4;yGq{3l`^4J3m;4C0_(UuC3@5E!+PZ!&s2Tqa_4fpcO;CB1dec{sV6#5c
2?1%<&f$I?*0^xm8bxl3z#vsQjuNzUjEjViO8TByr+NHC(){Q*J)>oN2l$Dr>#oIkepOWc511`MG%>dK?ejFEjO#Om>}ryijsa{h
^8W51=}prp5<I)+P_;`+E(YkB-Vb_^xh8D@ggH?h3>#>IcbIrUzHYT}cq64Fe~iTxm3Yl%NHh>;_ByrwD63F%^s2}6BOv-?h%$~p
(YE)z0c>&umz-Hwh`Fbf%4JalhE-2tPJIlb^lKl#&(rW>FO}t5y{KbAczrx~4y7}XS)c@L=`Pwt;>DRR=5Wn%{5BEL!Ld{{{Tl^6
h1!5sx+|zs`9lQk5J0S+YPw;D;w`yX^{RI_C+NH<89P@Kp52<R1H$>q)y4|N@#Nt^XQ%iDSyW>FqeA)TSHHAY7YBecCwo^x1DRmY
*+}El0^JI25p&(tvOKq3K~Wc~#6Bs=mx&;(^l8)`oovG=i70iumD}YI{3W%smHPcD(=mnl>Y5GGFGf$jEptZ(N7#V;5abgq)g329
%|QA!5Aa!B;JzcvNgkSPk@>2=9NNPPu1>d}cF6rU#xpyg$@Zg;?j`IQX~^r@LTcC0OP#_Y+&>0t33txq@wgdP-y!wAM~$Llvem79
(BDMSv-}AESy*{|mYl<7z7}41-iWlT6VD!cYp!stLpocq5hq5~I4Q|tII5d17!DDtz$#+t*^3WEqM8&0y<u>Jon1{&hq4IIPe<w8
1=P%+Fycw_M?+m;?vVELOw3Rj4J}Cr#wTbYe6TE1KYOiFJ{uWKgm>(_!U|z73ZSQ|*$#RB+c|@Ue*_M%|D(=K*F;VH4Bk*C-Aat(
7hn5k0ShxSU&LH77GgL5>e8H3FXDzy^sC>Sp8DR0V_rbi)>2r98S|ISbX|KY(AZ9laKNi^nTR;@^YGHUh_&qGErv03T=)wo$d|l{
$l74oaQ(i$ZJvn2X;C$d#I?Z*T8t*U^xEGx4}P_jFyCdg=qeq|`iB`&C%LsOZQ-ffp>J`o&Jk@Ib#Qy`C&>4uRfJB?DuJ=i;FW#u
)+3Kp?4<kf-1VneosXGd?dFu_xw~v@vh23gkO>>1QPJT}(du=NJZ!`QYr3CW&l+RyY_4U|>R>W6B896!(jK5{#R%ds(Fe_4l5NOu
xFTInG9;)1djYiOi6NYtzP9mxeKtH4U)YUv6tu%Tv_FX_nstRqNwxJ4GDu3_m<hv5u#4IXL30VKS}lrmP{C5RK6~Qo=0s0KWD7?a
NKnc&X?~w&8;GarvJ<CCZGN<mQ;MZPFkz6P5}OZHzfs?Rg}<^i(psi<;|6UX@XgzrCwO2aM6IJSm>ZF?Rh7hWp1#s!jiBkX7fAg)
{|}dwVr4+&v@=Yc#9PojL3H~z5r>}Y<S5e}MP!`5Nq2a`AUiFeb9I}=*|EBEzSJeN{n`U6Mhq6_Osj7Ng!JaNFThA6Q-?=iYHn@V
aG$u<5V5s$4HMF=XHD@r&1zXD+-H5Y?XKixubaTU$$-8tDTz|T^0DrS87)*NzM5U=vqv*s8%hj(rCGMn%waK<SoM>&kAj5;?5jl|
O_EHhzacE94}?8q4V+Tf=49oj6bqyaMj^Vt<(v0U3!(6(f$O+#bK>Oriq7J{Fc26-%xTFURVT^%>xSkArdd=hfQ2%3-t-WN1tX3*
rJu#{16{SeqdWt;ZmWq=kJkU)73fpq2rO`l8~#6uvpu&NzdV>5yY4>0{op7;OQYc8GF{d^#0Z?=$c5!I@OVEE>LO2+xwJ$WiG_JN
wy$ejdC$4w)S#J!Bb`BYOcU(ggof&ZQ{?67O3%6P;;hnHc?L<-3(h22Xo?YYw+{@NNA<a1?m1vcb1bFjuKfO@Gfy9A0CfZzPxNDA
9v6FPEpIk&TU=S5_}sb#nxeB0NgVJOiDyC08eGq~r6-rG4($1ZNiEN>Mc!;U-oC{{IV8Avy`maUF)eJSPS%P{cTmJMZZ9x~*GX6*
s+f{kvvsm1CI-gB&%Gy2TbNHu&yO(!clyXmTnP>6opZ7<I#USq^p2tU4ZYzlPNMF9FYg5ZbbX;qfw9)8?);PBBeN%Z2Nzj>{}xH}
UK{a3f=43p=yDidcp0gVE*oR5jAqE^NTbB188B1jJrfULMVOAiTJhwbnY<_-+)9MLpXJn9xb^n+DK<Q|VYLC(QNgy)*a3RRvwbc0
yda=d?!<HOi-lKlLbSOlDGV*#4hZx$QGp-xuc{zRxuSVHeuL}X*|!HAS&H`2sbz_fI=WWt7d!ahpepYMLWR_>O}n=LdUk(ds<Bs9
=xTG_$Q|)R4aE{|^F>s(`qZ9#kL-35mo7hoP#L>b@T*Z<>+?<>6K~nwG$7_E>6P-gbW37Qw02^dnC=$jX~XnSql)hfLM$Y2KIQ2r
+*GmN;>bXZ7)q(!91nfu03BF5Xe{*eX}iAmgP|3~7A4tdk90|koT5_%OOc{tKOjnD(ru<(jXyo<h(eC7y~qXYXV_wBMD`o;WWp?=
OgeM7Wu2efLL};1&&-bbBWcGX{oAJ+H&Q)}P9z*uCs5r6cR?H#ACd4O>qu!K!X^`Q4%}pNY~nH0Q`Bg|0XXHTUH!85T@O_YVN(?q
^-Sc-F3j-$wfJyq+ZIFVC%?dsm`&1gFf{w~Qa74Jy^AyfW(n~u<Q<5$6z{*lro;lF-zD4^8#n9UBa}KxO^wDFmqKhDxM9*5;zvV#
2jQq<{H_}ocyrD_39R|~rrNo!T4|r+=Qi`y`HtsgbUg0W-;E4G_`K$Nu~HCWK#PIa^|VYkZG|QxtYm#?F-F`wOaKBy*_ftI8PP$+
$Rr+B;#soGj^SDJjSK3w)0{hc@Z&{fhs`P7`y366JW&j%zObo0!}V|ecynq;@XL4l+iqr3C=g`BT8dNVBruQv;ps}G0qmW?A(T){
s7r;PY$;fKFO;r;YMXIq=2~V)OQS4_Pq9q%UinCp1G6`)l!qU!AvvF><X~$q<Sf8ljS-$H8fpqg!HGU$=O8O!6A~W>b?X$TE2u0e
kUuLmld1YdAu!p%r1<W`-OwZtzS__1K@TVf*kv0ArxaWdm8OMq2sU>OK`E^OR?}1hz=$0je*gI3SU?Pp+{2VYHCT2|6AK0W)D#Y2
KoxpxAbeDvBatd@YUQ-H1WVPN_iIDYrIu@{e6kJNKsv9n5@WJ-B=Rp&*0FcsrjQ@A=Kzv>`z^!Vi@=eIl-&8u&V*_@8jp6Y?NDu1
T3g5$<)^u;7SESVJ?!Z=$8;MpFMDbW)k;Aqk0$<wR}FsLL<toeR+vpc(0&f*(9GymJ3bul)D}Ja1@IU@h{#y~XVZt~61jEeaF#|5
a+v@bGps-`567BWDkm2r=G<!IvU8D>Tn6%XYP9R<jDwevvW_0Xq0wdS%>6e8`;rb%KhB<i6-#d`!UapT&v{o*z(hs03R!qzwi%of
e2aQ+=Y&k({D8^m@N;G8u}R*|CtaT!9G+K12stnI;zh(XwVYPII3Wz_g?YZsDlZI&IS<cg6n=-xWC&lmZrA+48cYVFfR?*cyY#Do
EvS>BC#fvTI^OWe0qO0Bl;tpz+;oBE1fXhte-%!O<OBz28D}7?zk>Blx9os4G`$3QNK5IYu35bif-g#L)=27NM^Tr1crW2;C1t8I
!qyS|J+Igf*vpc(^574SLs@aFtTuC^NhNSfIQJb0;KXMTBf~LIp)&IT7)`mi2h+92GC#9<?xa6xSvOY8WKo;S(=l@89HO{oAh_0U
x9(AV0A}>J^b3D_?BB0Xp#q}&DD!B1zBfKb*brt)f_NxzG7<UMr&9$^ki0d+TxY%ijjyeq77<lxy>h`la`v=|hi)aJmd;%BK_w@{
M|qJa-Vs{--4afX`qVv-Q~vSYC~{59Wv+QPWgg+LzVEu4*g?tDv%#CC1P)?!jwq9k6qSJf(O_h?sS8O8QV}9C1{G}=#tHbaK{5e=
3$w{X{gWP9+=ybQkaoaNhiD+F^`%0jwZmq@VF}n&ZSg`4`ecHmm8>ItbyiKqQ{py0Hi~uckO?iy3JDpEM(&hSPQy#O*#nOpM1M0R
-lW1+-;Y{m&2rm0V!#~}HFdC`$U~`gyHus|155z6+#vrqb|1ozqxnCa$0s@VtXHiS1n?6~UN$t-T@%IUD%D)ugAvhig%Ag)B0iza
a8Asu!i1Pe_67L=->~1d7D}UjEg48%@{Z-o#FQ5Tbc#g^H5xe~?g6Q9v%<?lnO39a^&s3%dp%`wR7sP6^7;$Y6QNVPTZ_cj0V44X
<o$<zSBP5FZ*q&A(CMUa6_}M>Gp;yF_ezEqLm2ZAal0GYb%-ILF2TypUtEnhPudLk1dVBnb$1UPj3_^fRO)%FH4AcG2hyE@cl1e$
o&Xa5Y^E~|@@4sK8I#?aLGXSh!>-oT1(>zHmuaP@*4ButJ}S(8DvfSSzmAmzikF%nj_30y^bgt0-<X-O?&Y^$LVdS2jP^@egxFcw
`VlO&fT(!v5jY$>TQYyqMUk20q_pZ>p4()VD*Q)p@pVQr7BnL;Lx?$3Q=GOENLEc>+A8(QokRima)|CT<gKNK`H(M+&J?q|$blFt
tGC03u8(<jw0&(DK|o0e4x$ny1ddGp^8H2wEgMBE*Ov9?<C(z#nBU)WM;(vIqY;rNSv_Q139}F|A*LRpfYJ`zv@+L?jW5=jFcGcD
%GFYbDjn>*3lU47@2X^UBZ06MjYYOV^KpgnxSli~jJl+O{7<T%2Aw!zb?*;93xEPG>f;Nrx$wsYXMIy2MYA~yYSyw->wZLVRXqhQ
=A%fMhrV9DJi(L(C=s^x|BqhiZrt}T-E0?wLiT^8e+_%`X(#zNDGF>t<<M}Ra)359o4LnC#6|pq-$)|{I;=i#^sv>a#_LOX)a;NP
Emhf@HReA|srEc6qF`w}jYJKM(1}#STiTO*;!V*l)_M}c9=%|#xTs_#E#=YnW7=+iKXD)k1BQ)+xu<@5e(cCG8SC&(de2Zu*J*3d
1}Oc}=@i$}2V$M0H-8#KxdL7VU>@bwx%YQYX<}w%NA=>jzxT}Cuv~wKA9#7#8Z!)WLeOvTV(5j`)U)u13BG)LnqtrOw))eh(K#!g
I`r)yC^crQBNh~m6yLo4K&DL?JklgfCy7A5O;-1PGv-)G)u$8(LB0qGQ;&+L0Kh0%3C5IHO|M@gLhJXMfFM!?KpR1{Bsq36GL)tt
=&ORO|K15%<GAdA6OXJU>ua+{2d>LC+DE1YjM0*G0M9)ds%wUm(&3r8E9;Nk<O$72%efel6L}!4m=fB30j~5|@=%htXi5buh$LBe
nR^rWv2Nu~<5YS$r9@2!5UU2yos>aF^V;Xzhb%KuggxG>RQe7iIji&$E`!Ar9pY9@CcMXf+IuI^N-d)3%cWuvq4N%h;-2^SCFz>)
0o<mMsy-?05)0Z8Plb}A*-lDq2y$<zB6-Z+Oh}~?LH)jF{9*uT7Jqu^1aP1tX5`*xBfPHrOv7oBCBudXbd-`oWus|!S4vKZKo(-}
=ey%W(;}-PEIY))bUmR}cNh^xX^*@Fsv)F4$RI5FL>-_aXcWIG7uzfrWdN<PcF!#5_*DAd%kVj~GUzX%YU8wr)4{nzP8!RfBroyX
J85xCoHSM4h_I~$i!}M&q$HI>W){=E%yRc}QQ&aK)@lo(58lnWEZ=)?z-dDtNAi(9CgA`_tZ3JyiICW7I&OYcw6G*YaI-8dbf+#R
=p}0Mds)8h^C<8xN95R2&5B77=h>xJWgt0Z#jjXL;y9a@;uXXCKRIu4D=t=sOR*XKO1&%p#-@RUo@zj_#5D8<9`wPLXkjDXKmMzE
J{jUBHhc|lbxLU(_9#unw(N)--vqT(Z6``m314h#dGqaL6aQz6+sh2AUU@oCWVlDU-kfvlp7(Owa79c3=*6RDtQQr79g&S%6ubTT
S@yv%q{fNnDx;#)ZxCPV9=@I3`U6uuw9OHNcLWe?cLMyQyMZc6!grb3V$|O;fyE%E=_`0Ml~mN79_9T1$jH(mKkP|^vq|T?hqM61
{&i=#maSF)gN<FDmNPGf`3r(RkVA^ZK}%{fWtl(`ktEI5j`!wkqVBc>*VsnHEtO56%IU++RPJN|-Hvlva~^Gj`x13xKQZXpG#rc%
?Uzn$Na&mQwB5d&P!271cd<;~s!+u+$dC%C<~DPGzcS!v`NcN*_l-=uMnL;2xJ~z1-Tv1Ax-^*~EMsTktS0&We+mxnHa@y{LSLk%
`SW|LM`n_%25OlwDoQn2B2h3693OrNUT+>)vU9#T2iZF$j~5)phUEexzy}Qqz_c$u(*Kt(pVs2T#t9ncs;=(^E?got9xb?3?Tw$T
ubJr(3`e+>dS>3Fs$9Ci|E=0HtpG&E7U7_}es?=wEP<v$ag@fMNTaZ*yJ~W^ZV6MsrH%d3fPHQ^!UA>W+yNK)2b&FAq7jN(pKcUw
;!!40pHzBJRtz7bUx6Xiu~KF4B<bE7{8>V_-xTb?XJtjG!^L={+em^9W6L-}`V^K=@ONn2nHF=4n~GvoN*=MS^95Lju~+cfo925G
hNv$746(mvfGWO04Ii);bo%ISu_WTd9P58<xJUbJSy<L5ZxhEwL2Jd@EWBV2To-UsFXu@|z+K+l_4P16#97SC5XpZh<;^z^(An-$
I~a2YYC2-emAgX#5POCxe<pe^G(N#gfa$H^4d}2N0LGqELtD_Z^qj4O>h)kHl8|A7R!%aBXuB|$*&scNChL<c2NfqN@BzI)yRWPh
ViG3S71Bx$rYJpKWFYLZBk?e-jF&t%=fG0H3$W0dP|j}qtJ{4U73D|;*J0ACeC8r^e?IeuaMuG}vb2LN?6jrw6I{E<FHPf=SBVJq
G4}4l{&K;-`{hu01NeVU*t1V}3vS}J{M)}^PuwkwYBfb8e6{Fc)o`@BmUx0yBD(Use2SC4swKn{cmNo4lldPeEJGGm1eMfFyzXw4
jklgz=#RnCh6d#>W&QmMGi*Z(z6W^E)Y0e#{iIgJRB6eHg!O9BU$EBr5*Vtme2TzUnetioqtR7l>W3(XU#~<h)@z0Xfj|hijkgh<
5-@hvoIU3QT&WKs82#*P%j)7v7_4i$&L3KoD<LKSROeK0>2fOTpgF`c%%6!JG(J4Lvdz{wKaNGV?3%1&p}tXWaF99JvdDzk8A?*G
<&TSw+IeNjEtg2|H0Z*qI<A$#C2aXuGy`v1^1!l}5%57&U2zB#Vb##LB)_C#HVLU*PEr=4-r!OrPujwxT!V(i#zN1OMezIA`qL^d
TGj;R5=qvlQi<j{2x(gGhtZlK8I@VNNq$jKv*YEVjT<uOvrggyD{AW*P6WwCa307UJy5Z4ErQ8lMGjSMH+0a~?hVuKxFNXB*UQsU
LsF#wY^ZblGZ*R`JzvZ3ssHfS?3FB_*oR996j}aE9lX!d+_AhCUQYmNWXb8~NK7386NuX_LA(U~<5I8x<*uC5yB?-koje8Q%a|eb
7{$3Z-GFX=1UR_ML1@f!K5JbCvGjKcQf2ZqVN=XKCo^U4>fH6&8&TQ&HdHVv4`n_iRf&yp^ZK95XEgZcp~D#3?{L>M1v~Ztpzeip
e94!Id35-W0)y#Z$uk+_!MCw1BAX7!J5S%Vw6PiAAg|R1NNPp1SdfEgJ7PW)WU)$WgcMu+$e$PB@w6u6GOSc{-6`55fw>ADY{Hc$
X<%ow$IxRHYp)>C!TCc&Vxp7$7O&#<V4RfdiS%X^6eOZ^aB*1x^`pWb*@DQDn8-8I<#<=Z{LMeoxD296<oMNZcxWHPJ`A`KxhoG)
*XgR4zpSt6HkLqf?ueyUKa_t@dy1EYe{}%MQh%^ZDAz>-{CNLdfxUb6U5CqW+cTlLdqCOqW?iP~sya7&Ewa($T(u=?w#bA<2Zovv
ND17?JrIb)oV(pa?m}}zunI7~Wl1X(dl$6vPifU%mE1zM*aX8CN2eoop?2tF%wqbaqz>g-+r$$zFB_L*$Lppd2%pTqVAHrIM;;K4
C_4)b5MBw(*!?Ri&|<PE|Cpw8J}iu6z_~%QXDYiB6U_3_PqgpF`#4;SQ|<-KlmdSGD_dPpzxF4iT@#hcV%08;r?1c2&)t)1AO@2S
Ym_2$EgbijRcRlw4$vPlnuwqy6jXTdMWXbmXBz#cmgrH%z$^{cwSoEcp-v*UTBKL3<p#qsEU0Ey`vnB}hfJbERwe7@4z{|s{ZQG+
Z;FZh!~M8%b7;vAAXcjXv#iC|s1#u|>$*iks82Eqv@GZlpQtdik-}%ZgAV;j&>KTh7NLo)_y(wW-%%AKNI;EMxaARPzq`ct>+DIN
W9TKvIsA^k=7>u6q;i!|urGw?9t*RY-_v&RKDyi$;Eu@ZvLdm|9_H29kg5J|JTx!eTc3|>Ka69gJ}+CBj`qMqf^d0|r^2&La5-Is
sBHx`Ya3+8j3Fiw-hF7(rKU90NYs>rLsNxamo5|}xl{(53Ph>oJyO9KsnA54hEzePPWH@AM|`^w<3d|)`bO>}&AW*XaP&uqQ&M#>
=Go(4t<R}-pR%M6UNXTZS(PxQ3GLYS?x-$WMJLZO?`a4MsCU`ilQL?~HSeYc4B5GzD_%ALQ%&g9w_^==dv>l}bySO$3;5d0;joS4
pCLzknZW9&drh&dvv@p!AIZ7`;mLMA<M_CW%%|H5>CW2F1N;QC-;vfb?}niT=^B`>o6^X$q2`MP?qohbhL<(uyz$@HxY&@j+d4xl
bq;^+rf`)G{spq4^;>=8Le-^1bgM}xcja3o?X16g5UMG^yh}n4>NgZ=tECP=+sryaNI%e>oaU0>f8DdP&>B*3<|_GCxwO3i)t7yu
kwSydv!$*{B}Uh$2^*YUG%^g4ZXX}~EDfe-LzUSbzT$uxgCWkz>7SCBfR#|N?eS%fDn~k2&X(8Co7kST7k!cT1I$<d0u$(rZa5M#
4g?Zr*{}Un_~IqZnWwbK+UD)7w~7^4q!+i=IRQ^`sp4wx-J*XeB|Xj(H#qZ%->;!)w#HPxzSnDap6<G#GS2Bh(Ae(=Clvc|%pRMZ
@{q<U+=6XN`pOrhh6j^S!Gn6fU&Ik;PFN?_nn_+U7E+*`ry-~iKKV4DPl?Mx85;g)`Dj$q!R!11{VfjGc#gLu%Ic@>`CU7Q^$8Rq
K^zqBP&Ks9biJJbH;=n^6YuXlG-dQC;|jdWp@$3HLg|ek6}|J=oToAt?p~vlkAv(i>I<vu$csl>NLr#Y`|sG@aAzax8?A+kLW8=&
Me~CEwb{`z;w2tDoAWn^j;6BcPN9dIO2lMU<GHF4#3{>Y2t@Cjdu{o56)mcoV3|Fu7I>DENpowmI!}9tU?}sLpMXPoF?q`Bg%ZTS
*CLwdp%`7cHq{lN097&GdVz>fdEFk(P-^O>H<%_HU~KE8J5owCbg%O@`?n#+So1#HzfJmKU8dtl7ruNj<rL%I!czE`Q*5X7B+=&s
Y@tmiB?+tvF=3$b!E+75?GF>}`Q9!9<W+~9V#y*Rt6NeO3!nZuWex{XTz%KCPS{|vJ%|2S`qDdxL9m{qdoozj){n>i5IC(psxJKm
L@?UTmQs$`^Pe7o=YG(Kp`Vn-Oo-tsnR16oZE`Uqj$OFO<Ki41nR|KFpxb6BD|M#o5n<*=$o&MK(Iv%7NLJ)3hdNbxDB6X1HtZ$t
gM9>q_ko;5s8?&XHc+vj5?WI3e}~)u05S^dpIeiJWZoO<3Xb1pk`Ng%yze9-`WfNZNck<wN1z3$Q->#Adzq~1SoVgmtzr=Q5Pz0p
ipp#wnSD;~wz{+a^V*>7Bw)r|=%`15iDSi4jkW>Yvxd!cdIjm$pig|cZ_C(mNRz0UgDT6*^8aPhXaM6i`2E-Zj#{_I=3~egq|o}P
O#0h~wmCf)PCvEtBXDg3&Q4b;NbqplBh;_equ~V6%=9mrMg(|-Vj|9rda;cmsp8F*4>{LZo5<)}3&VM?v*!|dDL%k{DlJ+P2phtx
2;C=>aZ*r*iXrc{n7Xrcu(w|Glkn-Uu3N73gqz3*mdr{H){ueGAcR7d2t&@;2Q`mOWsfd)Qg52`0e=N|);+fHWy`}5)n4F`*9P63
uHPS7V2+T(nfD$8sDMbw5{=!DxJYBiUvHGTle)?eic($#13TD19p1Iu@7OI-b=rjy4CDBjsyd{;xkOw>L5XXOdb1e?r+Fy)$s`6-
p|*KggLeKvA+X;do~xz{uM;8#kt&9Cc2ry*!g0owzSFZqUI;WWp-0aRc#m$^GsfsL%ModRpZWsZ0f5;`WcpjZ)#%EI&+cE5(DicW
28u3i?W_^!Ps9^Hry?ik-oP_p7Qw{+j`ULfg}0d{sB1cjR97b?FY0zf_5*&dW8-p-nf@jvh>j+|<$4(X=O_`26+Zf*fwIiuH^$2u
mQNF@8Kb)A(sDlqmNuF(emaaFd%hj$T=Uj7Mj0PHv&#bOugB<&oj{t)Ue}mO(hHG?vSb}h1r9T|286`AwnvW(biASBTU}157Z;WZ
xjKP_mO$OF7*(2zQ4qS;X~*|4bWkh*lbI6DfQ>DzM~pFP2j%PWW`R?+WUBvEUw&RN3ruopRf2e(hFAP`j<ClCGtnC#kC%(C$~=J7
Cf4j&AbyJ@h&}GCwreFzmr?+i5;w0T(X9$Z)H8MTj5R6E*5ys*g~%@2-gFj1Hl}pBuOvTmofc0^Snn-vfXDJ5bViVy4=-98Q{O|>
%rb_FSgDMr&@DYT8N!=;_r+(BOV9P>YLPvLNP!ghxwK4_>y7i6gc@oR#cd2ek-z|FBm>Tw6Lq8pSD}AD01zi+AB<H_pVUu(C$kgt
4~u1|@)|bAY4MnraM_4GmRMYsCzVGSn>!Uk%^pLO{d+j(d7+JbczlS`LU|uzrV#p#TE&?V@q9E3b=&U18i?g$B^ztMPzWm2!S^iv
EjVLEXC%JQAvF)XkyfiGYaM}qpb=4P=#QcQxKylsjq>+SE%Yr>nK1{2c}$%x$xPBkoC1{Gh0RgB^;XlQL1pmgU$_w-JM7%G5f9N3
Wz3gE7$d<!p51%NP*P4+J4thMpS~36*zy!Tqs^aonmuZhy(R1Phw%Ch<Q@|<tah<ZS1jNZVHl+K83Zy_&$@HZzEk_XsrFkx4FDj=
0qEU*-+Z9TtlzslafNJ);tDt)4gkC*DC@v>mIj%Baj<~aM3nq3(>8S;<}~xJxM&qi`i?u9REx+)Q#$ik8IhWMd?6>(DBrM3ga{-G
&nt>ikB9m|PAVS2k%;5e=MQtR6ueev#t~q8*#)dkVGf-p^Odpr+>F#MSd7jZrr4D=naP$%fa}<IqkS&RJVZGiG~r-%5R2zpCTUDK
Wmg+=qpcd(-*aqG-Br}>HL51eoU_B(imdv+OI-wN;~spNg-%npPMohRE|y<@@Z|ZkQZUOcc{>d|?PdoX$Z3cCyG<D=wpP<I<kNTz
i<yd=7oNA{^pbEhy9%t(^6jn4<cO&rG~hLH`NkQyi&cxHxfZ4mD0@RtsS^N8dXh$umy^Xw_@f1eJqt|GQTUA-8EPKWtkS*-DZtAe
K+wFE%mtlm<S6<rHsXJ3ws;v+JCs8@Aanxh<pJQA{$K?@&|g6d-A7>ob!@-{`_Y{LyVzULeR(oO`FCxw_i%^0C7d+?L-^_LxjB%&
PV4-MAuTTv2b85VOtuMii}SSv%5Hr@Zw^Qh1WoU<m?F?Ex_S-0z{SlfB+4LRJd}YDZpnkq)xT2N_1{^N<P0T~CGkZZ={;@lf+Cb=
-tl<*68ObtxP<qmT7W(^s<smCQj|Ap&6)-1`J*nAn-5PUou#-Kt^0-HdfQ%ts>D6-VZtmaO*k*hpNF?GJYY}&)3Ts)f_$yQSgW&#
Z9t5VmOeUoA3b+^+%6>#P4y(MCJn3s<xj4mu~SrbBa4{V9g*JLHsm~Wl2&=uSoa|#8t7RO8^x;P0Q~e3O(KBg2M2e$D?T@@faLl!
&7hH!Ps5t*{4Ewc*8N+O89o$80n`Ap-9Qq|Annzq)74W{gjufV;&y_lMMmZw=JD9=s5j-%i)e~zZIq;zgcI`&$g0_aj}dz4(a9dX
wW2ee>pehL*%0Ldnl#N8il57@AJ##bP_Hw6Ng)jWJWTZc%Z&)_&*l|D%F~_$S>0nJ6;$<N^+t=i4H?5wop;9Mv!Ur40<|~}q)34)
2jAxD9QOPWHjGl5l!M_U$Txl$j!@2!0b`!kvrbF)f_`0$MqL0nFa2`6gx1l<5*ja9H^m-RD3INyoc!o`vEilmVmVuAeT7MP*nyX8
E2t1Hktt$v``qGC<AzOtV86fQaSAqm7>)d?(Zgk*gjOwhyKUa3WO9BFfCkhgoDsIPqJscz3|4@U0vp5Bw3Sf4(In=*iUYsj7(O@4
R$W+i5Mopl{PLC-;w#}jkVVqxXnfKtsF!)D6}ah+>gdy;`&+*Bh$yAO8I}Sp6&vlu(%pl+W^bE1-2cxN|1WQD+Ts1|EZ(Xw8h!r^
Zp|KLfjue+%!dF$ky++h2d&v1xM;L2&ob_$_z0+_1isU{K*sX>(^=8#Go2j$NOKtbFcMJw&$Z65VQ`Ug02w&<Sm(^5vE3D{3*B8s
KiRx?2|ekz&KF$H5?MIHylX!6J;uum37u-qf-yB;Bh|-`z)tD0Wppf-?W};S7c*J~2Bmwd3Ow1Ck3u`iC;L*F3&cSGV7_!1y$Dh&
$u@BGuTNV2>W6cJzphC%jYZ5t!#Z&u*v|CCmfmWJpF&xgM!MJlDInWxFD-=8*9;;u+1P2oyU(Eeb@O-j*=a<ug6~X%Klrb70FZme
5@+#@OzG1L1b8X#Gq6npKxOg|j#7aa$m$Sgc3+W_EqjdvUc02twe6cRGVA^y>68CN_K@z;R^eXjc;c#e4lGNM%kARh&sXPOe_)*x
b+r|lB;^X`uNN?-kQz<!c$-i(@#D;|)cAkqNRv<PeCF~*()XM~52ZTqGuZ#U`-Z~qgSlZNRU|r-Tq?P8abh?(ki%>=L&U#TFU`$y
1c+;(k0K$6-r=I_6jE>}0^LO<6>3H2gyK*|GvYDQvtoCWK)}@m<V4!$q9U`T>LL-*?$6Q-mt}&x+zOg-snW02?fg=LK(Ssj5POTZ
=%)+hDmpEjw&zWJO7MU3ICAp*Z3ZzQhWl!Vzv=%a?wJz`#?A(SoO-doo-P4@?xC}Ls;H^U!m0OA<F46WYg@X;uSGfaPalQopZwF&
*IkwDs)!4hqprwq!POWiRTX_AWilhV9dBj<xthc71Zp6yXu}hO3fzmM$ZRqaB$=d@aL~v~+p<lDu>};Igr52E`*5}J`gCb!rKqbd
n7Xs*IC1l%u%}ww>`}Ha{*)E$B5#ts3x^gsYQMtn1bRwNC1L}(2<JDER*EOOVditCl>9Y&Ml#9fA<<Mem%|BVdK{vbV#v0kL>f3e
NX-_+SOES~^9mUcvECc^a*=o{Q9l}}XAkS*BtQkjF+Tf{5WYy`@rq`A82%9(382c&oK?`)`fs50Oi0A;K_k$mA5hq0lR1TqGnqH}
;J&qNZKmiUop1p`IL7Wz1}<|$wqz$Ec<r1!CBjqQkSo1`N%Gnv{XKsK>XtKsG;*4qTE{3NC^*J{WnbztEDgwO5l{1C;7f+}n;5&1
s$;yl24%k}O}^LtQ_i55vp~}gW0gk@EKO?dHF&%{NG|J-ijo`boiP;e$r5@;6cO}?WeK@q$ow?n@o7bM7t-C6vgGmlkTa08f%^#9
xSU+7`p`qFy0BiS>03Gc(@-y=$c7sUM$RtmUAs>BWsI=`pubdAO-`^Dc6w;%cDBg4lzk1}Vo(DYWl<@3{3iS}A<efMel|ot%_G4}
O$ttSP%xKSI~UecJM+9x#OE=#ZOd(KjdVcl<C5sf1AgJ#swl%Av(6;C-4Q0%`{a$`|LcA{KtT7Ttk508*D&A7mtz#<D^mcmlB9`@
t~zb@1#Z1Dn=v{E^H)K)6Ywi0AWx~oJ#X2YkFG|b!o+O$bQ8R+#DMZ`AsHS?5$be7+LaPP9h#D0;y>pweT=|=Kl!!|=qU%0H6OW?
<tL)-MtfjX>m0-k9epnr`8CYwM{cuLK?D*nueH$^v9d9awYL-XB}}2|UUAV{RZpkQOO7(Fb!iZEIgZ->b#_<ICto(;^O5wtsP$A$
8>W!*a%wldzg{m-{4{Bj{mW%&$I$Dlvp}aJLqVwoZgf}ENPTm9*d{x!8_B;{#wRC{-ocVEJ0a^Fcwv0n7Bbx^1Q_efi|sO30}54H
CB{K^N>CRU34;D3>7MEZNCJWvwbOz}>Jigvn|x;o#CfW+)5RH2N{I$tJr{K{^hqM@qAxO%d(U;{#4q_v1anBiGhz@GR}|iiAQ0KY
!y_G?aM_yUxB$ZfucTTm#EC?s28Tp7yOspth}z3&r<51ctD998Y!zv#P7KNZ5EFtr^KTEzdv}gA&@}`4OtSMRzXRg$gqnb+zfsBj
4B~JwqPnc7v{i8|XyfS>%mv^9LI67T!{?HDE|^0XT_yJ=0NmH;wFMhWgBCw1!L~#tGX$G}c}U0}24i@Z)5cr)2v1!bcu8wh>$TsB
zHhi-OTGm8H(#!!3xW;sAYf}bc%3j%rJamfI8rw+So#u4vsvzn(^@<OP}<q5B;TvZV;~?p|3s%=0^W+BkC}m+K(*(6jDG^5Hbr<F
yG9nZKx#sak9<m^QkJ~etcaqed&FBPq=sY%cjIF<vjm=OL7{<78vV@eN54bS=Rxf<VWShPQLmR=%E#U@e)sh^&Ft%nscwj1c`2QU
Z^We7;ZAzM?c#$ORq}LWM?ZWU-8-ePl)a8!nXSrAr<LD$F^<4uwlePs$q#<CrraJB$OTQ@SCk94cNrB%b2rO38?V9LpS@Wq0E6G4
*hA?+1WWVOarM+1^VPeC4V4E3R|kqmLq%`IRkK|Wjj-vM@n{h9kYr9XiO+Yt;cLq<LTR7TVW}TiC=x>5MH5gI4<M829d;@v!n%cg
gny1*3_k3`A~2W|J#~`;?bg5Q{Kb-6`HW6`QJ-JH_me=yO)=vrKyX+D`h~nEH=YXeXqH_-{A@UrB8l{MnzPjrAjRhb)tQH!$`Rf9
<lj_yAmz6qTPp&8Z7-MC%B1jx9ee>Jz<<LX?t8O)8G&0DH8!9Lx@Va?7KY4?QA@arz@UNs<{lU@AP(|xlru(VHgx=DNDZ)(VfC2A
7=E$><CqlHwU+D8<N)}MOa(Sl6D2xU4G*^=#mtZQ*J2-tIA_@^q_pqtJu%b-g6CvLTGQ4C9pHS{3s^(gettghU9bz^Xw@Is(Vz_Y
+i-JTlPBs&&scU@XUK-T2y-hF=XiJC52BkX5@|`Or2y}EafBp0`=m!a?qUv1A;aK@I!D}Fw|wGSc^r-&Nh`{dlm=qFPLhO+T`iF`
{zIe+W|&#-JLS<&l0_K^AHLP_Rsg>-s_v3P_Q33`KGj9vT3w17vz914LTXAstz3%8+}d)?`xT4Rof|)+$IWz!AD3UkoGD;x=yr+H
s$CxEIS7#<W^+Uzt-w&9Lczmyt))=Co0C~8Veu9&W8ysLU7YelA&eypsVU;@Djb2W8_0BBr6pjwO%ld4r(8Zj^6a^?Wp+6-^S@@C
g}@rlgpFu~A^l4&l%OJ_^p8Lg)BhWCy{J$`eNlAcfNRN=tyt>LnD0)2h<dK*JvGtm4G6l9pgy*@Pi8v*yWAD!AT3yCKca)R`MAp2
4gDm0gQR#XYk@xnTXz<3IfnWB-D>BhzrViE;5pTQV2Ti8TyhHyuQ~K^_7wF1`Ae7D*mW25iPe6-0<~^P`j^=~sB1dJ4M3_x4<!Gk
PjIEvy&IDh3(_Xh>bAz^nRLQPqnf^uV^vOuHQ$UTMmkuOd~|3T*15gDQBH|<+`UFp9Mfnf$eEIHd^7FUH<3Z=F2b#mOKC2`HKzN-
^mL;qsf=m^k048<m(uZUostDbouSMAl^c#2MJ2`_Hj}=Je8j55Z2i6~Fj$Emc!X7IX+IFz1y?|<F#3OiZuK=o{*5luec+`>+w<DI
ebcpP>nybGuCw+Zlkc$=h0R5FKRsB5P|zFOG^IILE7Pf(nKY)>VZQ-7!yjjjkO)gl7F~{iIe2Zau`&b%)hcxWloPrX*E?|{tljgA
7hJ1?u?!hytT~EcLUkF!IZxC`SC@8#A=@<XL1WBQ>4|w1B?MY9XM6k~^Q%8%N%ELvy~aVs@_&=Tv*`Nz1bZR7(OYP@0WK-swZ<4S
0=C{Xf$*d{E5RwR$9NzlW}oi<G)g*xwrMkm37;co+31K3QXw|6<|~vOz}@7O3jawU>IxsvA`gvI{rqRPk?TDTAkc!i!+riL1UpU9
iM^VaVhukU0Q>v)tV|qfNW!ZKL}bAa93s*R2g9~QYj;S%Akxj2DwmOcZYCv8ZIb{n*bfHF+~g@|Y){qzfrOv*k7^)yY66fF^N-)1
5A?n{i+P%oBTAO5nv!_EQ2y(V=PqMlSl7#?f%X+7v^J_SP=@lpJvLEVjxg;@o@%CoQJ2)7j?XDUn`Im?Nyeh1Ghn-eHm}S8?PxN(
;L>L&VQ8HVYx$j|jEJr^8d@&AP&$^zdQVrMaL0{7IhYd$Szh7zRHPmN0!p^OKt3AUqL!(g%*XgT=v)akxuj;AiRmV$HcV{dGqy5B
8_CDeQwNjwt&H7F#m`9#iCy0S1RJs269|%1`7-G8I?MALE3ZyeYu$}N=yU#x9==*#W6|$BLkX2<@49e=SK;z~8}6G+YJ<l5_K@*t
1!+*aE(A^e7~W*lL4Pkz0~?!G#12lic}u$BxJPo!HZu}g(SW*9DQvUGhz(t!6Ys=5)g9QY7yKsa4-m+6wH}$mH=6?O@g<Q4N&5KE
!zoQG1Z^AUegHrFr0O(D-d^*#%0&$SAnZ|*qno)K(?iUqy$bEA#AZ^t3Gv><Fq3%n>^ywxQ9NuM(u;I!WMYe`5e<r{_T4EIH$AnJ
b-OS#P@~e0Hy0bY$x-PA0}8pr6Ya?b^$ou^S4?ALpuu)$7GA{>tK+7737l3;ApFF9dc8$0r8HZ|kjE$+n!sY6?iK=f&)}xb73dxR
=p%$jL2({T23j#<OqByxv3}f&^VvInicJs+h_1cBX3s`&rN68X18}e{O$WL5Ia>+U^Kbqm0Rcu>9!E%Z9(%!M;|o+a^}nzFaFla1
ab5!FYsA>97f06PKS_qh;ofA{c<lOjT$omR-~Bqc^>6rP=9WgJc{Jx>R7vVt=bk!z9ci#YJxAn8p;#GI%KS9j^KU|V!J>er+khQw
GE1Xv_!h|ygx5=!3|9RsL6H%x--AZHaSIaBcTnPAy}6dM!t|NG+T1q(bIBLtRodFqu+77IUVErG+#&i-W8wsN{&?y?;)>IH15JUr
>-H~Jo@4-8+st*6=haYz(YLn}lZa?EPtz7YSj2=eZVB?1PdBvqxObuCxZm~E+FNyMb7<jFlKLes!C4-zRyE^Z+vEAZdmVG|GL8lP
q1=X4-B2eu-2($7SEcc|P(Mh3LUy=a+C=gz2nQU%=UX~W?YR$OtFj(wMddc01;u=zw6B4PD^k=sqqS3N6Sbhpr7+{AR0LK>WdP+6
!*-HI584NBoLQ;dkK$)#@DtGe!&~lPjyA!1hDjRVyt*h(<TK(Q3Iy?Yw3i5tAgpoIzBY0w=}%Cipj@NO_{jDq2CMFY3YlW5ZrzMQ
LG{=mQzs+b>`Vsgo?=b|7Y0MEi$U`L?7Ic7DA6DPXE(jUV5#Id@}NE+Xt=b5ql<k$<abIZ+(>y*NGv-L#9`ykU~|e304^qgzN+v<
mdN>{Vfy)uO(h)Q7C|BKoD~MTO;%b>*u@G;ybRNVX`MPYhz)VwcXLZcC!%p-b|Hl7I)WJco)K+}KXcfyb76)bh~>lMDfg3OwJ}#M
gp5vDBbHRBWZT<8vPb1LgKhEd`=>rrjsn-D<uf7WL28w-x0!vk3;a{0w44H#>Vs!s?<#dtlP7Mg<K0n(LlAUEyo%UcLcHHAk*a<x
<Eq}Y2|a4VIE%5m5B1F_XjLG*sviu~Uq$Qy?Vg)E=%%M&eyv0ol=(i#K{ai{*Y;d$(hvMV`RROI7RLWRAYOd9X!B#0%fT4SNz*Q&
0L4lCQZh_&zRtmP(FK5?-q#k=>S)JuC`f}1O0jSn#?fr?I(-rk=LexM+#h)DA=wzjA4)(Qcl%i}Nege)zL8NiMFkptllWz&oY$NR
uwa|?RYWVc$}3h_HuNQ{qauBYyy1sgDZ_uS0(_ewCj5B4oXxC{7_z>BmtGiqol05ljR=iB!?Bqe2WB_sK+ep(_wU}Kv?lyo{<Q$0
ArbCbP?+YH@ca}^tt#?amlJQ45w;Ww3uo`@t34cIAKV~vnmlPXAvx~w$_d*>OufkQ%CjPqj%B4LDY1dx(0f9{S2?5EbJ^y?E~K@~
UBZU}KHGxsT{}E|)qha{)j26q1;BFmhO2dT9<mI$co<^bIc=#rLWg5RjJi?d-;>~IaX)9SWO<Fi_4(R%&^8lc_+nPO5gPC^oWI3t
kQ2Rz(1tZo24TRhsH5}Fi=wSCF|B-7ib-b-&W_DR(0zkiUWXtcCSV&=tJbX12eIvoeL>INki4w5%JPslYW5<oh*cRQh$e($oc~2a
V}Uqz31!XHb-3g@DrftFfg2hD`OCnz`CM6Qn1JHBBErMe-~p)j{?wJfBmRE<gNdR12t1iB%ENvj91A8$=o0amtMaA^iI!#^hM*?$
Vm)BSJct->cR9hj9syqcump{w8zAF9riA$d7ZnFV;OSYWOO=x6x0|CxU+|-flzIV4PA4(Kt?jW`3Y_?_Og9>*+^B)Lc>OF`gVcQb
OFz-L1#(>9Syiyzv`bBjYN~M`f%TF&A26iJp{??qM^`;5ep-Ift1D30F%fC_-O`7k!hNGsGbDx?4pR6!&`Jw>71B9o;TyWUtck3Z
Sl46Q5TpMEum}zhuRJ0vAZKn9zPe~^=q4$JB1*sBv0QTK)VK?wP964Rs{MN3VF-KbWQsalBJE<&uyA%&nllXrWkvJn&~$i5j6P`a
b=2_MFuo+7ow8Rm<?pvjvUG3#yK;4^+EW(fihpH3f8vdvs~vI`1~cYQ=MljPhPcVaL*V3Jelxt%7`}3{H=1Fhrq|Z3Kxpp1^6*Gp
I`nOy-7v$y$rNslnC@oy(XpiTq(Fv(1%B;ldQEIUq&96EYYk~)>kZBr{2VSvC0EseF@<t`2q_|e76RQIW4DAT$Y&?kv%564l=flK
l$)E8)<UnxowDRlITV9cT1u!>6p5)$yyw9mGFJ6(<wp)0z#F0HJro}R%L}%P)lFfN-7`bJkS+dWn6A;RSrJttDL}Z&nr?Cp0^eXS
vUIatg>1&MXqGIQA=Fc!0){sr@`11m;0Cv3`-M}ysY@&P6Sg7y18$x|kLYQrnlBWX_(G<;qwDM3*=B-^Q72}O2xKwiOv!f?0Jc&2
A{6CmJ(r7?rvAIH5<B?4h}A*s6PTLTuy?deh4hSva(Pf4asU7T{7JQu-x%4O00H8*0f3+e+4i#;vBYQl0ssI200dcD
"""


def unpack(parent):
    data = base64.b85decode(''.join(encoded.split()))
    expected = '868abf1a5736c622848da8ad7fe48fe0ad94449319db1e08258175acb2d950a3'
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError('Переданные данные повреждены. Установка не начата.')
    folder = Path(tempfile.mkdtemp(prefix='karaoke-wifi-update-', dir=parent))
    folder.chmod(0o700)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:xz') as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts:
                raise RuntimeError('Неверный файл в комплекте. Установка не начата.')
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
            target.chmod(0o600)
    return folder


def main():
    ssh = os.environ.get('SSH_CONNECTION', '')
    if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
        raise RuntimeError('Выполните команду в SSH root@192.168.1.102.')
    folder = unpack('/root')
    unit = 'karaoke-wifi-update-' + str(time.time_ns())
    print('Комплект проверен:', folder, flush=True)
    print('Журнал установки:', unit, flush=True)
    result = subprocess.run([
        'systemd-run', '--unit=' + unit, '--wait', '--collect',
        '--setenv=SSH_CONNECTION=' + ssh,
        '/usr/bin/python3', '-u', str(folder / 'install.py')])
    subprocess.run(['journalctl', '-u', unit, '--no-pager', '-o', 'cat'])
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
