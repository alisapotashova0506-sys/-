python3 - <<'PY'
import base64
import hashlib
import os
from pathlib import Path

ssh = os.environ.get('SSH_CONNECTION', '')
if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
    raise RuntimeError('Выполните блок в SSH root@192.168.1.102.')

encoded = r"""
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
"""
data = base64.b85decode(''.join(encoded.split()))
if hashlib.sha256(data).hexdigest() != '6b48940e81d2773a89c9114600d1b77afc63086e26b560f76902fcee1ed88eeb':
    raise RuntimeError('Часть 2 повреждена при вставке. Повторите этот блок.')
folder = Path('/root/karaoke-wifi-transfer-868abf1a')
folder.mkdir(mode=0o700, exist_ok=True)
folder.chmod(0o700)
target = folder / 'part2.bin'
target.write_bytes(data)
target.chmod(0o600)
print('Часть 2/3 принята: 8000 байт.', flush=True)

PY
