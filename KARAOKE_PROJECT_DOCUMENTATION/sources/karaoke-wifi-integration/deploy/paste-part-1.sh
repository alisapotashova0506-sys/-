python3 - <<'PY'
import base64
import hashlib
import os
from pathlib import Path

ssh = os.environ.get('SSH_CONNECTION', '')
if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
    raise RuntimeError('Выполните блок в SSH root@192.168.1.102.')

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
"""
data = base64.b85decode(''.join(encoded.split()))
if hashlib.sha256(data).hexdigest() != 'b0d3ab67d555a424c85708fccc135772e7fae4a7385e831c54387488ae5c2907':
    raise RuntimeError('Часть 1 повреждена при вставке. Повторите этот блок.')
folder = Path('/root/karaoke-wifi-transfer-868abf1a')
folder.mkdir(mode=0o700, exist_ok=True)
folder.chmod(0o700)
target = folder / 'part1.bin'
target.write_bytes(data)
target.chmod(0o600)
print('Часть 1/3 принята: 8000 байт.', flush=True)

PY
