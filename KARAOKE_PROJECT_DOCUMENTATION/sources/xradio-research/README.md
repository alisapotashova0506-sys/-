# XRadio investigation — 2026-10-14

This is an experimental source patch, not an installable or runtime-validated fix.

Observed device failure: xradio_bh Oops in queued_spin_lock_slowpath, LR wsm_get_tx+0x6b4/0x8fc; later NetworkManager RCU stall in xradio_remove_interface.

Build inputs:
- User-supplied config-6.6.44-current-sunxi64.
- Linux stable v6.6.44 from https://github.com/gregkh/linux.
- Armbian build de1a1959827c3a274d5b7d52c474e4dd373ae3ef from https://github.com/sicXnull/armbian-build.
- All 424 enabled entries in patch/kernel/archive/sunxi-6.6/series.conf applied successfully.
- XRadio 3a1f77fb2db248b7d18d93b67b16e0d6c91db184 from https://github.com/fifteenhex/xradio, as pinned in that Armbian build.
- Cross compiler Debian GCC 11.3.0; original device compiler Ubuntu GCC 11.4.0. Binutils 2.44 versus original 2.38.

Candidate: initialise vif_lock in xradio_add_interface before publishing the vif; remove subsequent spin_lock_init of the same lock from xradio_vif_setup. This prevents publication-before-initialisation and reinitialisation while a BH consumer may hold/wait for the lock. Other lifecycle races are not ruled out.

Validation: baseline and candidate each compiled all 17 driver objects and linked xradio_wlan.o successfully for AArch64. No module was installed, loaded, or functionally tested. Module metadata linking and exported-symbol compatibility have not been validated.

Limits: original build marked dirty; local patches unknown. olddefconfig drops external-driver options whose driver trees were not added, changes toolchain-derived options, and enables RELR support for the newer linker. Compile success does not establish ABI compatibility with the running device. Need original xradio_wlan.ko to compare the faulting instruction and function layout before proposing device tests. No AP activation should be attempted as part of this artifact.

## Comparison with uploaded original module

Original module SHA256: 87f8bb37c1e4509a761477bfa701a0733a0caa894a3160acf0a192680da403e3.
The complete .text section of the original module and reconstructed baseline object is byte-for-byte identical; SHA256 of both sections: 21456b9c3cd41cb970f1f3acac18c098d63ef2a85e5082580d651e5c2b0ae979.
Original wsm_get_tx+0x6b4 is the return address after queued_spin_lock_slowpath for the vif_lock acquisition, preceding the enabled check.
Original add_interface publishes vif at .text offset 0x11908 and calls vif_setup at 0x11964; vif_setup zeroes vif_lock at 0x112fc.
This establishes the suspect lifecycle sequence exists in the installed binary, but does not establish that the candidate fixes all failures.

A candidate .ko was linked in /tmp for analysis with KBUILD_MODPOST_WARN=1 because the full-kernel Module.symvers is unavailable. This converted 125 missing export-resolution checks to warnings; it did not validate compatibility. Original and candidate have the same 125 undefined symbols and same vermagic. The candidate depends field is empty rather than mac80211,cfg80211 because provider information is missing. No module was installed or loaded. This candidate is NOT ready for installation; further export/provider and module-layout checks and an independent recovery path are required.

## Remaining AP failure analysis — 2026-10-15

Device runtime: the two-instruction v2 patch prevented the reproduced AP-switch Oops in subsequent tests; AP association, DHCP, intermittent HTTP200, and AP-to-station rollback were observed. Stable AP transport was not verified. Samsung and Intel3168 Windows both failed; Windows had direct WiFi route,99% signal,DHCP .100.68 but no gateway ARP entry. AP channel1 and6 tests and AP outbound legacy-rate restriction did not yield stable operation. Local root and monitor endpoint HTTP200 in77ms and7ms.

Second confirmed binary/source defect: wsm_suspend_resume_indication declares arg uninitialized. For XR819 AP on vif0, break skips arg.link_id assignment. Original assembly uses uninitialized sp+224. xradio_suspend_resume passes link_id to xradio_ps_notify for unicast firmware stop/resume events; tx confirmation requeue marks real station asleep, while scheduler masks asleep links. Bad link_id can lose wake notifications and strand TX. This matches intermittent data-plane symptoms but actual firmware event state was not captured, so causation is not established. Candidate source correction initializes arg={0}; compilation of all affected code and linking driver object passed. It has not been installed or runtime tested and full per-link bitmap semantics remain unverified.

Additional defects, not proven causes: link_id_after_dtim/link_id_uapsd never initialized; link_map_cache pointer-array indexed as per-link count in AP link allocator; RX_ENC_HT incorrectly ORed into rx_status.flag instead of encoding. CCMP MIC path qualification limits claimed effect of last issue. Avoid treating these as a verified fix bundle. No new device changes made during this analysis.
