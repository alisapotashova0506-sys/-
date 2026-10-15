python3 - <<'PY'
import base64
import hashlib
import os
from pathlib import Path

ssh = os.environ.get('SSH_CONNECTION', '')
if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
    raise RuntimeError('Выполните блок в SSH root@192.168.1.102.')

encoded = r"""
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
data = base64.b85decode(''.join(encoded.split()))
if hashlib.sha256(data).hexdigest() != '57ac87b47cf13179a98f763af4843bfa75b51f4b233b95e8f32421ed8f48f74b':
    raise RuntimeError('Часть 3 повреждена при вставке. Повторите этот блок.')
folder = Path('/root/karaoke-wifi-transfer-868abf1a')
folder.mkdir(mode=0o700, exist_ok=True)
folder.chmod(0o700)
target = folder / 'part3.bin'
target.write_bytes(data)
target.chmod(0o600)
print('Часть 3/3 принята: 7432 байт.', flush=True)

import io
import subprocess
import tarfile
import tempfile
import time

parts = [folder / ('part' + str(n) + '.bin') for n in (1, 2, 3)]
if not all(part.is_file() for part in parts):
    raise RuntimeError('Переданы не все части. Установка не начата.')
data = b''.join(part.read_bytes() for part in parts)
encoded = base64.b85encode(data).decode('ascii')
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

PY
