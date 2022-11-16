; Free RAM notes
; $06F8-$06F9: Used to store edge table addresses
; $06FA-$06FB: Used to store target edge IDs
; $06FC-$06FD: Used for custom walk destination after transitions
; $0703: Used to flag forced transitions
; $0704-$0705: Used to store terrain type at the start of a transition

org $aa8000 ;150000
db $4f, $52 ;OR
OWMode:
dw 0
OWFlags:
dw 0
org $aa8010
OWReserved:
dw 0

;Hooks
org $02a929
OWDetectTransitionReturn:

org $02a939
OverworldHandleTransitions_SpecialTrigger:
JSL OWDetectEdgeTransition
BCS OWDetectTransitionReturn

org $02a999
jsl OWEdgeTransition : nop #4 ;LDA $02A4E3,X : ORA $7EF3CA

org $04e8ae
JSL OWDetectSpecialTransition
RTL : NOP

org $02e809
JSL OWSpecialExit

org $02bfe8
JSL OWAdjustExitPosition

org $02c1a9
JSL OWEndScrollTransition

org $04E881
Overworld_LoadSpecialOverworld_RoomId:
org $04E8B4
Overworld_LoadSpecialOverworld:

org $07982A
Link_ResetSwimmingState:


; mirror hooks
org $02FBAB
JSL OWMirrorSpriteRestore : NOP
org $05AF75
Sprite_6C_MirrorPortal:
jsl OWPreserveMirrorSprite : nop #2 ; LDA $7EF3CA : BNE $05AFDF
org $05AFDF
Sprite_6C_MirrorPortal_missing_mirror:
JML OWMirrorSpriteDelete : NOP ; STZ $0DD0,X : BRA $05AFF1
org $0ABFBF
JSL OWMirrorSpriteOnMap : BRA + : NOP #6 : +

; whirlpool shuffle cross world change
org $02b3bd
jsl OWWhirlpoolUpdate ;JSL $02EA6C
org $02B44E
jsl OWWhirlpoolEnd ; STZ.b $11 : STZ.b $B0

; flute menu cancel
org $0ab7af ;LDA $F2 : ORA $F0 : AND #$C0
jml OWFluteCancel2 : nop
org $0ab90d ;JSL $02E99D
jsl OWFluteCancel

; allows Frog sprite to spawn in LW and also allows his friend to spawn in their house
org $068a76 ; < 30a76 - sprite_prep.asm:785 (LDA $7EF3CA : AND.w #$40)
lda $1b : eor.b #1 : nop #2

; allows Frog to be accepted at Blacksmith
org $06b3ee ; < 333ee - sprite_smithy_bros.asm:347 (LDA $7EF3CC : CMP.b #$08 : BEQ .no_returning_smithy_tagalong)
jsl OWSmithAccept : nop #2
db #$b0 ; BCS to replace BEQ

; load Stumpy per screen's original world, not current world flag
org $06907f ; < 3107f - sprite_prep.asm:2170 (LDA $7EF3CA)
lda $8a : and.b #$40

; override Link speed with Old Man following
org $09a32e ; < bank_09.asm:7457 (LDA.b #$0C : STA.b $5E)
jsl OWOldManSpeed

; Dark Bonk Rocks Rain Sequence Guards (allowing Tile Swap on Dark Bonk Rocks)
;org $09c957 ; <- 4c957
;dw #$cb5f ; matches value on Central Bonk Rocks screen

; override world check when spawning mirror portal sprite in Crossed OWR
org $0283dc
jsl.l OWLightWorldOrCrossed

; override world check when viewing overworld (incl. title screen portion)
org $0aba6c  ; < ? - Bank0a.asm:474 ()
jsl.l OWMapWorldCheck16 : nop

; Mixed Overworld Map
org $0ABA99
WorldMap_LoadDarkWorldMap:
LDA.b $10 : CMP.b #$14 ; attract module
BEQ .vanilla_light
    LDA.l OWMode+1 : AND.b #!FLAG_OW_MIXED : BNE .mixed
        LDA.b $8A : AND.b #$40
        BEQ .vanilla_light
    .mixed
    PHB : PHK : PLB
        JSL LoadMapDarkOrMixed
    PLB
.vanilla_light ; $0ABAB5

;(replacing -> LDA $8A : AND.b #$40)
org $00d8c4  ; < ? - Bank00.asm:4068 ()
jsl.l OWWorldCheck
org $02aa36  ; < ? - Bank02.asm:6559 ()
jsl.l OWWorldCheck
org $02aeca  ; < ? - Bank02.asm:7257 ()
jsl.l OWWorldCheck16 : nop
org $02b349  ; < ? - Bank02.asm:7902 ()
jsl.l OWWorldCheck
org $02c40a  ; < ? - Bank02.asm:10547 ()
jsl.l OWWorldCheck
org $05afd9  ; < ? - sprite_warp_vortex.asm:60 ()
jsl.l OWWorldCheck
org $07a3f0  ; < ? - Bank07.asm:5772 () ; flute activation/use
jsl.l OWWorldCheck
org $07a967  ; < ? - Bank07.asm:6578 ()
jsl.l OWWorldCheck
org $07a9a1  ; < ? - Bank07.asm:6622 ()
jsl.l OWWorldCheck
org $07a9ed  ; < ? - Bank07.asm:6677 ()
jsl.l OWWorldCheck
org $07aa34  ; < ? - Bank07.asm:6718 ()
jsl.l OWWorldCheck
org $08d408  ; < ? - ancilla_morph_poof.asm:48 ()
jsl.l OWWorldCheck
org $0bfeab  ; < ? - Bank0b.asm:36 ()
jsl.l OWWorldCheck16 : nop
org $0cffb6  ; < ? - ?.asm ? ()
jsl.l OWWorldCheck16 : nop
org $0cffe8  ; < ? - ?.asm ? ()
jsl.l OWWorldCheck16 : nop
org $1beca2  ; < ? - palettes.asm:556 ()
jsl.l OWWorldCheck16 : nop
org $1bed95  ; < ? - palettes.asm:748 ()
jsl.l OWWorldCheck16 : nop

org $02b16e  ; AND #$3F : ORA 7EF3CA
and #$7f : eor #$40 : nop #2

org $06AD4C
jsl.l OWBonkDrops : nop #4

;Code
org $aa8800
OWTransitionDirection:
dw 3, 2, 1, 0 ; $02 after $02A932
OWEdgeDataOffset:
dw OWSouthEdges, OWEastEdges, OWSouthEdges
OWCoordIndex: ; Horizontal 1st
db 2, 2, 0, 0 ; Coordinate Index $20-$23
OWOppCoordIndex: ; Horizontal 1st
db 0, 0, 2, 2 ; Coordinate Index $20-$23
OWBGIndex: ; Horizontal 1st
db 0, 0, 6, 6 ; BG Scroll Index $e0-$eb
OWOppBGIndex: ; Horizontal 1st
db 6, 6, 0, 0 ; BG Scroll Index $e0-$eb
OWCameraIndex: ; Horizontal 1st
db 4, 4, 0, 0 ; Camera Index $0618-$61f
OWOppCameraIndex: ; Horizontal 1st
db 0, 0, 4, 4 ; Camera Index $0618-$61f
OWOppSlotOffset: ; Amount to offset OW Slot
db 8, -8, 1, -1 ; OW Slot x2 $700
OWOppDirectionOffset: ; Amount to offset coord calc
db $10, $f0, $02, $fe
OWCameraRangeIndex:
db 2, 2, 0, 0 ; For OWCameraRange
OWCameraRange:
dw $011E, $0100 ; Length of the range the camera can move on small screens
OWAutoWalk:
db $04, $08, $01, $02

DivideByTwoPreserveSign:
{
    asl : php : ror : plp : ror : rtl
}

OWWorldCheck:
{
    phx
        ldx $8a : lda.l OWTileWorldAssoc,x
    plx : and.b #$ff : rtl
}
OWWorldCheck16:
{
    phx
        ldx $8a : lda.l OWTileWorldAssoc,x
    plx : and.w #$00ff : rtl
}
OWMapWorldCheck16:
{
    lda $10 : cmp #$0014 : beq .return ; attract module, return with Z flag cleared
        jsl OWWorldCheck16
    .return
    rtl
}

OWWhirlpoolUpdate:
{
    jsl $02ea6c ; what we wrote over
    ldx $8a : ldy #$03 : jsr OWWorldTerrainUpdate
    rtl
}

OWWhirlpoolEnd:
{
    STZ.b $B0 ; what we wrote over
    LDA.w $0703 : BEQ .normal
        LDA.b #$3C : STA.w $012E ; play error sound before forced transition
        RTL
    .normal
    STZ.b $11 ; end whirlpool transition
    RTL
}

OWMirrorSpriteOnMap:
{
    lda.w $1ac0,x : bit.b #$f0 : beq .continue
        lda.b #$00 : rtl
    .continue
    ora.w $1ab0,x
    ora.w $1ad0,x
    ora.w $1ae0,x
    rtl
}
OWPreserveMirrorSprite:
{
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq .vanilla ; if OW Crossed, skip world check and continue
        lda.b $10 : cmp.b #$0f : beq .vanilla ; if performing mirror superbunny
            rtl
    
    .vanilla
    lda.l InvertedMode : beq +
        lda.l CurrentWorld : beq .deleteMirror
        rtl
    + lda.l CurrentWorld : bne .deleteMirror
        rtl

    .deleteMirror
    lda.b $10 : cmp.b #$0f : bne +
        jsr.w OWMirrorSpriteMove ; if performing mirror superbunny
    + pla : pla : pla : jml Sprite_6C_MirrorPortal_missing_mirror
}
OWMirrorSpriteMove:
{
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq +
        lda.w $1acf : ora.b #$40 : sta.w $1acf
    + rts
}
OWMirrorSpriteBonk:
{
    jsr.w OWMirrorSpriteMove
    lda.b #$2c : jml SetGameModeLikeMirror ; what we wrote over
}
OWMirrorSpriteDelete:
{
    stz.w $0dd0,x ; what we wrote over
    jsr.w OWMirrorSpriteMove
    jml Sprite_6C_MirrorPortal_dont_do_warp
}
OWMirrorSpriteRestore:
{
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq .return
        lda.l InvertedMode : beq +
            lda.l CurrentWorld : beq .return
            bra .restorePortal
        + lda.l CurrentWorld : bne .return
        
    .restorePortal
    lda.w $1acf : and.b #$0f : sta.w $1acf
    
    .return
    rep #$30 : lda.w $04AC ; what we wrote over
    rtl
}
OWLightWorldOrCrossed:
{
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq ++
        lda.l InvertedMode : beq +
            lda #$40
        + rtl
    ++ jsl OWWorldCheck : rtl
}

OWFluteCancel:
{
    lda.l OWFlags+1 : and #$01 : bne +
        jsl FluteMenu_LoadTransport : rtl
    + lda $7f5006 : cmp #$01 : beq +
        jsl FluteMenu_LoadTransport
    + lda #$00 : sta $7f5006 : rtl
}
OWFluteCancel2:
{
    lda $f2 : ora $f0 : and #$c0 : bne +
        jml FluteMenu_HandleSelection_NoSelection
    + inc $0200
    lda.l OWFlags+1 : and #$01 : beq +
    lda $f2 : cmp #$40 : bne +
        lda #$01 : sta $7f5006
    + rtl 
}
OWSmithAccept:
{
    lda FollowerIndicator : cmp #$07 : beq +
    cmp #$08 : beq +
        clc : rtl
    + sec : rtl
}
OWOldManSpeed:
{
    lda $1b : beq .outdoors
        lda $a0 : and #$fe : cmp #$f0 : beq .vanilla ; if in cave where you find Old Man
        bra .normalspeed
    .outdoors
        lda $8a : cmp #$03 : beq .vanilla ; if on WDM screen

    .normalspeed
    lda $5e : cmp #$0c : rtl
        stz $5e : rtl

    .vanilla
    lda #$0c : sta $5e ; what we wrote over
    rtl
}

LoadMapDarkOrMixed:
{
    CMP.b #!FLAG_OW_MIXED : REP #$30 : BEQ .mixed
        LDX.w #$03FE ; draw vanilla Dark World (what we wrote over)
        .copy_next
            LDA.w $D739,X : STA.w $1000,X ; DB is $0A
            DEX : DEX : BPL .copy_next
        BRL .end
    .mixed
        LDX.b $8A
        LDA.l OWTileWorldAssoc,X
        STA.b $00
        LDY.w #$139C
        LDX.w #$003F
        .next_screen
            PHX
            LDA.l OWTileWorldAssoc,X
            EOR.b $00
            AND.w #$0040
            BEQ .light
                TYX : BRA .copy_screen
            .light
                TXA : AND.w #$0024 : LSR : TAX
                TYA : SEC : SBC.l LWQuadrantOffsets,X
                TYX : TAY
            .copy_screen ; more efficient to have X on the right side
            LDA.w $C739+$00,Y : STA.b $00,X
            LDA.w $C739+$02,Y : STA.b $02,X
            LDA.w $C739+$20,Y : STA.b $20,X
            LDA.w $C739+$22,Y : STA.b $22,X
            LDA.w $C739+$40,Y : STA.b $40,X
            LDA.w $C739+$42,Y : STA.b $42,X
            LDA.w $C739+$60,Y : STA.b $60,X
            LDA.w $C739+$62,Y : STA.b $62,X
            TXY : PLX
            DEY : DEY : DEY : DEY ; move one screen left
            TXA : AND.w #$0007 : BNE .same_row
                TYA : SEC : SBC.w #$0060 : TAY ; move one screen row up
            .same_row
            DEX
        BPL .next_screen
    .end
    SEP #$30
    LDA.b #$15 : STA.b $17 ; what we wrote over
    RTL

    LWQuadrantOffsets:
    dw $1000-$0210 ; top left
    dw $0C00-$01F0 ; top right
    dw 0,0,0,0,0,0
    dw $0800+$01F0 ; bottom left
    dw $0400+$0210 ; bottom right
}

; Y = sprite slot index of bonk sprite
OWBonkDrops:
{
    CMP.b #$D8 : BEQ +
        RTL
    + LDA.l OWFlags+1 : AND.b #!FLAG_OW_CROSSED : BNE +
        JSL.l Sprite_TransmuteToBomb : RTL
    +

    ; loop thru rando bonk table to find match
    PHB : PHK : PLB
    LDA.b $8A
    LDX.b #(41*6) ; 41 bonk items, 6 bytes each
    - CMP.w OWBonkPrizeData,X : BNE +
        INX
        LDA.w $0D10,Y : LSR A : LSR A : LSR A : LSR A
        EOR.w $0D00,Y : CMP.w OWBonkPrizeData,X : BNE ++ ; X = row + 1
            BRA .found_match
        ++ DEX : LDA.b $8A
    + CPX.b #$00 : BNE +
        PLB : RTL
    + DEX : DEX : DEX : DEX : DEX : DEX : BRA -

    .found_match
    INX : LDA.w OWBonkPrizeData,X : PHX : PHA ; S = FlagBitmask, X (row + 2)
    LDX.b $8A : LDA.l OverworldEventDataWRAM,X : AND 1,S : PHA : BNE + ; S = Collected, FlagBitmask, X (row + 2)
        LDA.b #$1B : STA $12F ; JSL Sound_SetSfx3PanLong ; seems that when you bonk, there is a pending bonk sfx, so we clear that out and replace with reveal secret sfx
    +
    LDA 3,S : TAX : INX : LDA.w OWBonkPrizeData,X
    PHA : INX : LDA.w OWBonkPrizeData,X : BEQ +
        ; multiworld item
        DEX : PLA ; X = row + 3
        JMP .spawn_item
    + DEX : PLA ; X = row + 3

    .determine_type ; A = item id ; S = Collected, FlagBitmask, X (row + 2)
    CMP.b #$B0 : BNE +
        LDA.b #$79 : JMP .sprite_transform ; transform to bees
    + CMP.b #$42 : BNE +
        JSL.l Sprite_TransmuteToBomb ; transform a heart to bomb, vanilla behavior
        JMP .mark_collected
    + CMP.b #$34 : BNE +
        LDA.b #$D9 : CLC : JMP .sprite_transform ; transform to single rupee
    + CMP.b #$35 : BNE +
        LDA.b #$DA : CLC : BRA .sprite_transform ; transform to blue rupee
    + CMP.b #$36 : BNE +
        LDA.b #$DB : CLC : BRA .sprite_transform ; transform to red rupee
    + CMP.b #$27 : BNE +
        LDA.b #$DC : CLC : BRA .sprite_transform ; transform to 1 bomb
    + CMP.b #$28 : BNE +
        LDA.b #$DD : CLC : BRA .sprite_transform ; transform to 4 bombs
    + CMP.b #$31 : BNE +
        LDA.b #$DE : CLC : BRA .sprite_transform ; transform to 8 bombs
    + CMP.b #$45 : BNE +
        LDA.b #$DF : CLC : BRA .sprite_transform ; transform to small magic
    + CMP.b #$B4 : BNE +
        LDA.b #$E0 : CLC : BRA .sprite_transform ; transform to big magic
    + CMP.b #$B5 : BNE +
        LDA.b #$E1 : CLC : BRA .sprite_transform ; transform to 5 arrows
    + CMP.b #$44 : BNE +
        LDA.b #$E2 : CLC : BRA .sprite_transform ; transform to 10 arrows
    + CMP.b #$B1 : BNE +
        LDA.b #$AC : BRA .sprite_transform ; transform to apples
    + CMP.b #$B2 : BNE +
        LDA.b #$E3 : BRA .sprite_transform ; transform to fairy
    + CMP.b #$B3 : BNE .spawn_item
        INX : INX : LDA.w OWBonkPrizeData,X ; X = row + 5
        CLC : ADC.b #$08 : PHA
        LDA.w $0D00,Y : SEC : SBC.b 1,S : STA.w $0D00,Y
            LDA.w $0D20,Y : SBC.b #$00 : STA.w $0D20,Y : PLX
        LDA.b #$0B : SEC ; BRA .sprite_transform ; transform to chicken
    
    .sprite_transform
    STA.w $0E20,Y
    TYX : JSL.l Sprite_LoadProperties
    BEQ +
        ; these are sprite properties that make it fall out of the tree to the east 
        LDA #$30 : STA $0F80,Y ; amount of force (related to speed)
        LDA #$10 : STA $0D50,Y ; eastward rate of speed
        LDA #$FF : STA $0B58,Y ; expiration timer
    +

    .mark_collected ; S = Collected, FlagBitmask, X (row + 2)
    PLA : BNE + ; S = FlagBitmask, X (row + 2)
        LDX.b $8A : LDA.l OverworldEventDataWRAM,X : ORA 1,S : STA.l OverworldEventDataWRAM,X
        
        REP #$20
			LDA.l TotalItemCounter : INC : STA.l TotalItemCounter
        SEP #$20
    + JMP .return

    ; spawn itemget item
    .spawn_item ; A = item id ; Y = tree sprite slot ; S = Collected, FlagBitmask, X (row + 2)
    PLX : BEQ + : LDA.b #$00 : STA.w $0DD0,Y : JMP .return ; S = FlagBitmask, X (row + 2)
        + LDA 2,S : TAX : INX : INX
        LDA.w OWBonkPrizeData,X : STA.l !MULTIWORLD_SPRITEITEM_PLAYER_ID
        DEX

        LDA.b #$01 : STA !REDRAW

        LDA.b #$EB
        STA.l $7FFE00
        JSL Sprite_SpawnDynamically+15 ; +15 to skip finding a new slot, use existing sprite

        ; affects the rate the item moves in the Y/X direction
        LDA.b #$00 : STA.w $0D40,Y
        LDA.b #$0A : STA.w $0D50,Y

        LDA.b #$20 : STA.w $0F80,Y ; amount of force (gives height to the arch)
        LDA.b #$FF : STA.w $0B58,Y ; stun timer
        LDA.b #$30 : STA.w $0F10,Y ; aux delay timer 4 ?? dunno what that means

        LDA.b #$00 : STA.w $0F20,Y ; layer the sprite is on

        ; sets OW event bitmask flag, uses free RAM
        PLA : STA.w $0ED0,Y ; S = X (row + 2)
        
        ; determines the initial spawn point of item
        PLX : INX : INX : INX
        LDA.w $0D00,Y : SEC : SBC.w OWBonkPrizeData,X : STA.w $0D00,Y
            LDA.w $0D20,Y : SBC #$00 : STA.w $0D20,Y

        LDA.b #$01 : STA !REDRAW : STA !FORCE_HEART_SPAWN
        
        PLB : RTL

    .return
    PLA : PLA : PLB : RTL
}

org $aa9000
OWDetectEdgeTransition:
{
    STZ.w $06FC
    LDA.l OWMode : ORA.l OWMode+1 : BEQ .vanilla
        JSR OWShuffle
        LDA.w $06FA : BMI .special
    .vanilla
    REP #$31 : LDX.b $02 : LDA.b $84 ; what we wrote over
    RTL
    .special
    REP #$30
    AND.w #$0003 : TAY : ASL : TAX
    LDA.w #$007F : STA.w $06FA
    JSR OWLoadSpecialArea
    SEC
    RTL
}
OWDetectSpecialTransition:
{
    STZ.w $06FC
    LDA.l OWMode : BEQ .normal
    TXA : AND.w #$0002 : LSR
    STA.w $0704
    LDA.l OWSpecialDestIndex,X : BIT.w #$0080 : BEQ .switch_to_edge
    AND.w #$0003 : TAY : ASL : TAX
    .normal
    JSR OWLoadSpecialArea
    .return
    RTL

    .switch_to_edge
    STA.w $06FA
    LDA.l OWEdgeDataOffset,X : STA.w $06F8
    PLA : SEP #$30 : PLA ; delete 3 bytes from stack
    JSL Link_CheckForEdgeScreenTransition : BCS .return ; Link_CheckForEdgeScreenTransition
    LDA.l Overworld_CheckForSpecialOverworldTrigger_Direction,X : STA.b $00 : CMP.b #$08 : BNE .hobo
        LSR : STA.b $20 : STZ.b $E8 ; move Link and camera to edge
        LDA.b #$06 : STA.b $02
        STZ.w $0418
        BRA .continue
    .hobo
        STA.b $02 : STA.w $0418
        ASL : STA.b $22 : STZ.b $E2 ; move Link and camera to edge
        LDA.b #$0A : STA.b $23 : STA.b $E3
    .continue
    STZ.b $03
    ; copied from DeleteCertainAncillaeStopDashing at $028A0E
    JSL Ancilla_TerminateSelectInteractives
    LDA.w $0372 : BEQ .not_dashing
        STZ.b $4D : STZ.b $46
        LDA.b #$FF : STA.b $29 : STA.b $C7
        STZ.b $3D : STZ.b $5E : STZ.w $032B : STZ.w $0372 : STZ.b $5D
    .not_dashing
    PLA : REP #$31 : PLA ; delete 3 bytes from stack
    LDX.b $02
    LDA.b $84
    JML OverworldHandleTransitions_SpecialTrigger+6
}
OWEdgeTransition:
{
    LDA.l OWMode : ORA.l OWMode+1 : BEQ .unshuffled
    LDY.w $06FA : CPY.b #$7F
    BEQ .unshuffled
        REP #$10
        LDX.w $06F8
        PHB : PHK : PLB
            JSR OWNewDestination
        PLB
        SEP #$30
        RTL

    .unshuffled
    LDA.l Overworld_ActualScreenID,X : ORA.l CurrentWorld ; what we wrote over
    TAX : LDA.l OWMode+1 : AND.b #!FLAG_OW_MIXED : BEQ .vanilla
        LDA.l OWTileWorldAssoc,X : CMP.l CurrentWorld : BEQ .vanilla ; if dest screen mismatches the current world
            TXA : EOR #$40 : RTL

    .vanilla
    TXA : RTL
}
OWSpecialExit:
{
    PHY
    LDY.b #$00
    LDA.w $0418 : LSR : BNE +
        LDY.w $0704 : BRA ++
    +
    LDA.w $0704 : BNE ++
        LDY.b #$02
    ++
    JSR OWWorldTerrainUpdate
    PLY
    LDA.l $7EFD40,X ; what we wrote over
    RTL
}
OWShuffle:
{
    ;determine direction of edge transition
    phx : lsr.w $0700
    tyx : lda.l OWTransitionDirection,X : sta.w $0418

    .setOWID
    ;look up transitions in current area in table OWEdgeOffsets
    ;offset is (8bytes * OW Slot ID) + (2bytes * direction)
    asl : rep #$20 : and.w #$00ff : pha : sep #$20 ;2 bytes per direction

    lda $8a : tax : lda.l OWTileWorldAssoc,X : eor.l CurrentWorld : beq +
        ; fake world, will treat this OW area as opposite world
        txa : eor.b #$40 : tax
    + txa : and #$40 : !add $700 : rep #$30 : and #$00ff : asl #3

    adc 1,S : tax
    asl $700 : pla
    ;x = offset to edgeoffsets table
    
    sep #$20 : lda.l OWEdgeOffsets,x : and #$ff : beq .noTransition : pha ;get number of transitions
    ;s1 = number of transitions left to check
    
    inx : lda.l OWEdgeOffsets,x ;record id of first transition in table
    ;multiply ^ by 16, 16bytes per record
    sta $4202 : lda #16 : sta $4203 ;wait 8 cycles
    pla ;a = number of trans
    rep #$20
    and #$00ff
    ldx $4216 ;x = offset to first record

    .nextTransition
    pha
        jsr OWSearchTransition_entry : bcs .newDestination
        txa : !add #$0010 : tax
    pla : dec : bne .nextTransition : bra .noTransition

    .newDestination
    pla : sep #$30 : plx : rts

    .noTransition
    sep #$30 : plx
    lda.b #$7f : sta.w $06fa

    .return
    rts
}
OWSearchTransition:
{
    .exitloop ; moved here because of branch distance
    clc : rts

    .entry
    ;A-16 XY-16
    lda $418 : bne + ;north
        lda.l OWNorthEdges,x : dec
        cmp $22 : !bge .exitloop
        lda.l OWNorthEdges+2,x : cmp $22 : !blt .exitloop
            ;MATCH
            lda.l OWNorthEdges+14,x : tay ;y = record id of dest
            lda.l OWNorthEdges+12,x ;a = current terrain
            ldx.w #OWSouthEdges ;x = address of table
            bra .matchfound
    + dec : bne + ;south
        lda.l OWSouthEdges,x : dec
        cmp $22 : !bge .exitloop
        lda.l OWSouthEdges+2,x : cmp $22 : !blt .exitloop
            ;MATCH
            lda.l OWSouthEdges+14,x : tay ;y = record id of dest
            lda.l OWSouthEdges+12,x ;a = current terrain
            ldx.w #OWNorthEdges ;x = address of table
            bra .matchfound
    + dec : bne + ; west
        lda.l OWWestEdges,x : dec
        cmp $20 : !bge .exitloop
        lda.l OWWestEdges+2,x : cmp $20 : !blt .exitloop
            ;MATCH
            lda.l OWWestEdges+14,x : tay ;y = record id of dest
            lda.l OWWestEdges+12,x ;a = current terrain
            ldx.w #OWEastEdges ;x = address of table
            bra .matchfound
    + lda.l OWEastEdges,x : dec ;east
        cmp $20 : !bge .exitloop
        lda.l OWEastEdges+2,x : cmp $20 : !blt .exitloop
            ;MATCH
            lda.l OWEastEdges+14,x : tay ;y = record id of dest
            lda.l OWEastEdges+12,x ;a = current terrain
            ldx.w #OWWestEdges ;x = address of table

    .matchfound
    stx $06f8 : sty $06fa : sta $0704 : sec : rts
    plx : pla : pea $0001 : phx
    sec : rts
}
OWNewDestination:
{
    tya : sta $4202 : lda #16 : sta $4203 ;wait 8 cycles
    rep #$20 : txa : nop : !add $4216 : tax ;a = offset to dest record
    lda.w $0006,x : sta $06 ;set coord
    lda.w $0008,x : sta $04 ;save dest OW slot/ID
    lda.w $000a,x : sta $84 ;VRAM

    ;;22	e0	e2	61c	61e - X
    ;;20	e6	e8	618	61a - Y
    ;keep current position if within incoming gap
    lda.w $0000,x : and #$01ff : pha : lda.w $0002,x : and #$01ff : pha
    ldy $20 : lda $418 : dec #2 : bpl + : ldy $22
    + tya : and #$01ff : cmp 3,s : !blt .adjustMainAxis
    dec : cmp 1,s : !bge .adjustMainAxis
        inc : pha : lda $06 : and #$fe00 : !add 1,s : sta $06 : pla

        ; adjust and set other VRAM addresses
        lda.w $0006,x : pha : lda $06 : !sub 1,s 
        jsl DivideByTwoPreserveSign : jsl DivideByTwoPreserveSign : jsl DivideByTwoPreserveSign : jsl DivideByTwoPreserveSign : pha ; number of tiles
        lda $418 : dec #2 : bmi +
            pla : pea $0000 : bra ++ ;pla : asl #7 : pha : bra ++ ; y-axis shifts VRAM by increments of 0x80 (disabled for now)
        + pla : asl : pha ; x-axis shifts VRAM by increments of 0x02
        ++ lda $84 : !add 1,s : sta $84 : pla : pla

    .adjustMainAxis
    LDA $84 : SEC : SBC #$0400 : AND #$0F00 : ASL : XBA : STA $88 ; vram
    LDA $84 : SEC : SBC #$0010 : AND #$003E : LSR : STA $86

    LDA.w $000F,X : AND.w #$00FF : STA.w $06FC ; position to walk to after transition (if non-zero)

    LDY.w #$0000
    LDA.w $000C,X : AND.w #$0001 : BEQ + ; check if going to water transition
    LDA.w $0704 : AND.w #$0001 : BNE ++ ; check if coming from water transition
        INY : BRA ++
    +
    LDA.w $0704 : BEQ ++ ; check if coming from water transition
        LDY.w #$0002
    ++
    STY.b $08

    pla : pla : sep #$10 : ldy $418
    ldx OWCoordIndex,y : lda $20,x : and #$fe00 : pha
        lda $20,x : and #$01ff : pha ;s1 = relative cur, s3 = ow cur
    lda $06 : and #$fe00 : !sub 3,s : pha ;set coord, s1 = ow diff, s3 = relative cur, s5 = ow cur
    lda $06 : and #$01ff : !sub 3,s : pha ;s1 = rel diff, s3 = ow diff, s5 = relative cur, s7 = ow cur
    lda $06 : sta $20,x : and #$fe00 : sta $06 ;set coord
    ldx OWBGIndex,y : lda $e2,x : !add 1,s : adc 3,s : sta $e2,x
    ldx OWCameraIndex,y : lda $618,x : !add 1,s : adc 3,s : sta $618,x
    ldx OWCameraIndex,y : lda $61a,x : !add 1,s : adc 3,s : sta $61a,x
    pla : jsl DivideByTwoPreserveSign : pha
    ldx OWBGIndex,y : lda $e0,x : !add 1,s : sta $e0,x : pla
    ldx OWBGIndex,y : lda $e0,x : !add 1,s : sta $e0,x : pla
    pla : pla

    ;fix camera unlock
    lda $e2,x : !sub $06 : bpl +
        pha : lda $06 : sta $e2,x
        ldx.w OWCameraIndex,y : lda $0618,x : !sub 1,s : sta $0618,x
        lda $061a,x : !sub 1,s : sta $061a,x : pla
        bra .adjustOppositeAxis
    + lda $06 : ldx.w OWCameraRangeIndex,y : !add.w OWCameraRange,x : sta $06
    ldx.w OWBGIndex,y : !sub $e2,x : bcs .adjustOppositeAxis
        pha : lda $06 : sta $e2,x
        ldx.w OWCameraIndex,y : lda $0618,x : !add 1,s : sta $0618,x
        lda $061a,x : !add 1,s : sta $061a,x : pla

    .adjustOppositeAxis
    ;opposite coord stuff
    rep #$30 : lda OWOppDirectionOffset,y : and #$00ff : bit #$0080 : beq +
        ora #$ff00 ;extend 8-bit negative to 16-bit negative
    + pha : cpy #$0002 : lda $700 : !bge +
        and #$00f0 : pha : lda $04 : asl : and #$0070 : !sub 1,s : tax : pla : txa
        !add 1,s : tax : pla : txa : asl : asl : asl : asl : asl : pha : bra ++
    + and #$000f : pha : lda $04 : asl : and #$000f : !sub 1,s : !add 3,s
        sep #$10 : tax : phx : ldx #$0 : phx : rep #$10 : pla : plx : plx : pha
    
    ++ sep #$10 : ldx OWOppCoordIndex,y : lda $20,x : !add 1,s : sta $20,x ;set coord
    ldx OWOppBGIndex,y : lda $e2,x : !add 1,s : sta $e2,x
    ldx OWOppCameraIndex,y : lda $618,x : !add 1,s : sta $618,x
    ldx OWOppCameraIndex,y : lda $61a,x : !add 1,s : sta $61a,x
    ldx OWOppBGIndex,y : lda $e0,x : !add 1,s : sta $e0,x
    lda $418 : asl : tax : lda $610,x : !add 1,s : sta $610,x : pla

    sep #$30 : lda $04 : and #$3f : !add OWOppSlotOffset,y : asl : sta $700
    
    ; crossed OW shuffle and terrain
    ldx $05 : ldy $08 : jsr OWWorldTerrainUpdate

    lda $05 : sta $8a
    rep #$30 : rts
}
OWLoadSpecialArea:
{
    LDA.l Overworld_LoadSpecialOverworld_RoomId,X : STA.b $A0
    JSL Overworld_LoadSpecialOverworld ; sets M and X flags
    TYX
    LDY.b #$00
    CPX.b #$01 : BNE + ; check if going to water transition
    LDA.w $0704 : BNE ++ ; check if coming from water transition
        INY : BRA ++
    +
    LDA.w $0704 : BEQ ++ ; check if coming from water transition
        LDY.b #$02
    ++
    LDA.l OWSpecialDestSlot,X : TAX
    JSR OWWorldTerrainUpdate
    .return
    RTS
}
OWWorldTerrainUpdate: ; x = owid of destination screen, y = 1 for land to water, 2 for water to land, 3 for whirlpools and 0 else
{
    LDA.l OWMode+1 : AND.b #!FLAG_OW_CROSSED : BEQ .not_crossed
    LDA.l OWTileWorldAssoc,x : CMP.l CurrentWorld : BNE .crossed
    .not_crossed
        JMP .normal
    .crossed
        sta.l CurrentWorld ; change world

        ; moving mirror portal off screen when in DW
        cmp #0 : beq + : lda #1
        + cmp.l InvertedMode : bne +
            lda $1acf : and #$0f : sta $1acf : bra .playSfx ; bring portal back into position
        + lda $1acf : ora #$40 : sta $1acf ; move portal off screen
        
        .playSfx
        lda #$38 : sta $012f ; play sfx - #$3b is an alternative

        ; toggle bunny mode
        lda MoonPearlEquipment : bne .nobunny
        lda.l InvertedMode : bne .inverted
            lda CurrentWorld : bra +
            .inverted lda CurrentWorld : eor #$40
        + and #$40 : beq .nobunny

            LDA.w $0703 : BEQ + ; check if forced transition
                CPY.b #$03 : BEQ .end_forced_whirlpool
                LDA.b #$17 : STA.b $5D
                LDA.b #$01 : STA.w $02E0 : STA.b $56
                LDA.w $0703 : BRA .end_forced_edge
            +
            CPY.b #$01 : BEQ .auto ; check if going from land to water
            CPY.b #$02 : BEQ .to_bunny_reset_swim ; bunny state if swimming to land
            LDA.b $5D : CMP.b #$04 : BNE .to_bunny ; check if swimming
            .auto
                PHX
                LDA.b #$01
                LDX.b $5D : CPX.b #$04 : BNE +
                    INC
                +
                STA.w $0703
                CPY.b #$03 : BEQ .whirlpool
                    LDA.b #$01 : STA.w $0345
                    LDX.w $0418
                    LDA.l OWAutoWalk,X : STA.b $49
                    STZ.b $5D
                    PLX
                    BRA .to_pseudo_bunny
                .whirlpool
                    PLX : RTS
            .to_bunny_reset_swim
            LDA.b $5D : CMP.b #$04 : BNE .to_bunny ; check if swimming
                JSL Link_ResetSwimmingState
                STZ.w $0345
            .to_bunny
            LDA.b #$17 : STA.b $5D
            .to_pseudo_bunny
            LDA.b #$01 : STA.w $02E0 : STA.b $56
            RTS

        .nobunny
        lda $5d : cmp #$17 : bne + ; retain current state unless bunny
            stz $5d
        + stz $02e0 : stz $56

    .normal
    LDA.w $0703 : BEQ .not_forced ; check if forced transition
        CPY.b #$03 : BEQ .end_forced_whirlpool
            .end_forced_edge
            STZ.b $49 : STZ.w $0345
        .end_forced_whirlpool
        STZ.w $0703
        CMP.b #$02 : BNE +
            DEC : STA.w $0345 : STZ.w $0340
            LDA.b #$04 : BRA .set_state
        +
        CMP.b #$03 : BNE ++
            LDA.b #$17
            .set_state
            STA.b $5D
        ++
        RTS
    .not_forced
    CPY.b #$02 : BNE + ; check if going from water to land
        LDA.b $5D : CMP.b #$04 : BNE .return ; check if swimming
            JSL Link_ResetSwimmingState
            STZ.w $0345
            STZ.b $5D
    +
    CPY.b #$01 : BNE .return ; check if going from land to water
    LDA.b $5D : CMP.b #$04 : BEQ .return ; check if swimming
        LDA.b #$01 : STA.w $0345
        LDA.l FlippersEquipment : BEQ .no_flippers ; check if flippers obtained
        LDA.b $5D : CMP.b #$17 : BEQ .no_flippers ; check if bunny
            LDA.b #$04 : STA.b $5D : STZ.w $0340 : RTS
        .no_flippers
            PHX
            INC : STA.w $0703
            LDX.w $0418
            LDA.l OWAutoWalk,X : STA.b $49
            PLX
            LDA.b $5D : CMP.b #$17 : BNE .return ; check if bunny
                LDA.b #$03 : STA.w $0703
                STZ.b $5D
    .return
    RTS
}
OWAdjustExitPosition:
{
    LDA.w $06FC : CMP.b #$60 : BEQ .stone_bridge
    CMP.b #$B0 : BNE .normal
        LDA.b #$80 : STA.b $20 : STZ.b $21
        BRA .normal
    .stone_bridge
        LDA.b #$A0 : STA.b $E2
        LDA.b #$3D : STA.w $061C
        LDA.b #$3B : STA.w $061E
        INC.b $23 : INC.w $061D : INC.w $061F
    .normal
    LDA.w $0703 : BEQ +
        LDA.b #$3C : STA.w $012E ; play error sound before forced transition
    +
    INC.b $11 : STZ.b $B0 ; what we wrote over
    RTL
}
OWEndScrollTransition:
{
    LDY.w $06FC : BEQ .normal
        CMP.w $06FC
        RTL
    .normal
    CMP.l Overworld_FinalizeEntryOntoScreen_Data,X ; what we wrote over
    RTL
}

;Data
org $aaa000
OWEdgeOffsets:
;2 bytes per each direction per each OW Slot, order is NSWE per value at $0418
;AABB, A = offset to the transition table, B = number of transitions
dw $0000, $0000, $0000, $0000 ;OW Slot 00, OWID 0x00 Lost Woods
dw $0000, $0000, $0000, $0001 ;OW Slot 01, OWID 0x00
dw $0000, $0001, $0001, $0000 ;OW Slot 02, OWID 0x02 Lumberjack
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0101
dw $0000, $0000, $0101, $0000
dw $0000, $0000, $0000, $0201
dw $0000, $0000, $0201, $0000

dw $0000, $0102, $0000, $0000
dw $0000, $0301, $0000, $0000
dw $0101, $0401, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0301
dw $0000, $0000, $0301, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0501, $0000, $0000 ;Zora

dw $0302, $0602, $0000, $0000
dw $0501, $0801, $0000, $0402
dw $0601, $0902, $0402, $0602
dw $0000, $0000, $0602, $0801
dw $0000, $0000, $0801, $0901
dw $0000, $0b03, $0901, $0a03
dw $0000, $0000, $0a03, $0d02
dw $0701, $0000, $0d02, $0000

dw $0802, $0000, $0000, $0000 ;OW Slot 18, OWID 0x18 Kakariko
dw $0a01, $0000, $0000, $0000
dw $0b02, $0000, $0000, $0f01
dw $0000, $0000, $0f01, $0000
dw $0000, $0000, $0000, $0000
dw $0d03, $0e01, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0000

dw $0000, $0000, $0000, $0000
dw $0000, $0f01, $0000, $1001
dw $0000, $0000, $1001, $0000
dw $0000, $1001, $0000, $0000
dw $0000, $1101, $0000, $1101
dw $1001, $1201, $1101, $0000
dw $0000, $1301, $0000, $0000
dw $0000, $1401, $0000, $0000

dw $0000, $0000, $0000, $1201
dw $1101, $0000, $1201, $1301
dw $0000, $1502, $1301, $0000
dw $1201, $1701, $0000, $1403
dw $1301, $1801, $1403, $1701 ;Links
dw $1401, $1901, $1801, $1802 ;Hobo
dw $1501, $1a02, $1902, $0000
dw $1601, $0000, $0000, $0000

dw $0000, $0000, $0000, $0000 ;OW Slot 30, OWID 0x30 Desert
dw $0000, $0000, $0000, $0000
dw $1702, $0000, $0000, $1a01
dw $1901, $1c01, $1b01, $1b03
dw $1a01, $1d01, $1c03, $0000
dw $1b01, $0000, $0000, $0000
dw $1c02, $0000, $0000, $0000
dw $0000, $1e02, $0000, $0000

dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $1e02
dw $0000, $0000, $1f02, $2002
dw $1e01, $0000, $2102, $2201
dw $1f01, $0000, $2301, $2301
dw $0000, $0000, $2401, $0000
dw $0000, $0000, $0000, $2402
dw $2002, $0000, $2502, $0000

dw $0000, $0000, $0000, $0000 ;OW Slot 40, OWID 0x40 Skull Woods
dw $0000, $0000, $0000, $2601
dw $0000, $2001, $2701, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $2701
dw $0000, $0000, $2801, $0000
dw $0000, $0000, $0000, $2801
dw $0000, $0000, $2901, $0000

dw $0000, $2102, $0000, $0000
dw $0000, $2301, $0000, $0000
dw $2201, $2401, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $2901
dw $0000, $0000, $2a01, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $2501, $0000, $0000

dw $2302, $2602, $0000, $0000
dw $2501, $2801, $0000, $2a02
dw $2601, $2902, $2b02, $2c02
dw $0000, $0000, $2d02, $2e01
dw $0000, $0000, $2f01, $2f01
dw $0000, $2b03, $3001, $3003
dw $0000, $0000, $3103, $3302
dw $2701, $0000, $3402, $0000

dw $2802, $0000, $0000, $0000 ;OW Slot 58, OWID 0x58 Village of Outcasts
dw $2a01, $0000, $0000, $0000
dw $2b02, $0000, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $2d03, $2e01, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0000

dw $0000, $0000, $0000, $0000
dw $0000, $2f01, $0000, $3501
dw $0000, $0000, $3601, $0000
dw $0000, $3001, $0000, $0000
dw $0000, $3101, $0000, $3601
dw $3001, $3201, $3701, $0000
dw $0000, $3301, $0000, $0000
dw $0000, $3401, $0000, $0000

dw $0000, $0000, $0000, $3702
dw $3101, $0000, $3802, $3901
dw $0000, $3502, $3a01, $0000
dw $3201, $3701, $0000, $3a03
dw $3301, $3801, $3b03, $3d01
dw $3401, $3901, $3e01, $3e02
dw $3501, $3a02, $3f02, $0000
dw $3601, $0000, $0000, $0000

dw $0000, $0000, $0000, $0000 ;OW Slot 70, OWID 0x70 Mire
dw $0000, $0000, $0000, $0000
dw $3702, $0000, $0000, $4001
dw $3901, $3c01, $4101, $4103
dw $3a01, $3d01, $4203, $0000
dw $3b01, $0000, $0000, $0000
dw $3c02, $0000, $0000, $0000
dw $0000, $3e02, $0000, $0000

dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $0000
dw $0000, $0000, $0000, $4402
dw $3e01, $0000, $4502, $4601
dw $3f01, $0000, $4701, $4701
dw $0000, $0000, $4801, $0000
dw $0000, $0000, $0000, $4802
dw $4002, $0000, $4902, $0000

dw $0000, $4001, $0000, $0000
dw $0000, $0000, $0000, $4a01
dw $0000, $4101, $0000, $0000

OWSpecialDestSlot:
db $80, $80, $81

org $aaa800 ;PC 152800
OWNorthEdges:
;   Min    Max   Width   Mid OW Slot/OWID VRAM Terrain Dest Index
dw $00a0, $00a0, $0000, $00a0, $0000, $0000, $0000, $B040 ;Lost Woods (exit only)
dw $0458, $0540, $00e8, $04cc, $0a0a, $0000, $0000, $0000
dw $0f38, $0f60, $0028, $0f4c, $0f0f, $0000, $0000, $2041 ;Waterfall (exit only)
dw $0058, $0058, $0000, $0058, $1010, $0000, $0000, $0001
dw $0178, $0178, $0000, $0178, $1010, $0000, $0000, $0002
dw $0388, $0388, $0000, $0388, $1111, $0000, $0000, $0003
dw $0480, $05b0, $0130, $0518, $1212, $0000, $0000, $0004
dw $0f70, $0f90, $0020, $0f80, $1717, $0000, $0000, $0005
dw $0078, $0098, $0020, $0088, $1818, $0000, $0000, $0006 ;Kakariko
dw $0138, $0158, $0020, $0148, $1818, $0000, $0000, $0007
dw $02e8, $0348, $0060, $0318, $1819, $0000, $0000, $0008
dw $0478, $04d0, $0058, $04a4, $1a1a, $0000, $0000, $0009
dw $0510, $0538, $0028, $0524, $1a1a, $0000, $0000, $000a
dw $0a48, $0af0, $00a8, $0a9c, $1d1d, $0000, $0000, $000b
dw $0b28, $0b38, $0010, $0b30, $1d1d, $0000, $0001, $000c
dw $0b70, $0ba0, $0030, $0b88, $1d1d, $0000, $0000, $000d
dw $0a40, $0b10, $00d0, $0aa8, $2525, $0000, $0000, $000e
dw $0350, $0390, $0040, $0370, $2929, $0000, $0000, $000f
dw $0670, $06a8, $0038, $068c, $2b2b, $0000, $0000, $0010
dw $0898, $09b0, $0118, $0924, $2c2c, $0000, $0000, $0011 ;Links House
dw $0a40, $0ba0, $0160, $0af0, $2d2d, $0000, $0000, $0012
dw $0c70, $0c90, $0020, $0c80, $2e2e, $0000, $0000, $0013
dw $0f70, $0f80, $0010, $0f78, $2f2f, $0000, $0000, $0014
dw $0430, $0468, $0038, $044c, $3232, $0000, $0000, $0015
dw $04d8, $04f8, $0020, $04e8, $3232, $0000, $0000, $0016
dw $0688, $06b0, $0028, $069c, $3333, $0000, $0000, $0017
dw $08d0, $08f0, $0020, $08e0, $3434, $0000, $0000, $0018
dw $0a80, $0b40, $00c0, $0ae0, $3535, $0000, $0000, $0019
dw $0d38, $0d58, $0020, $0d48, $3536, $0000, $0001, $001a
dw $0d90, $0da0, $0010, $0d98, $3536, $0000, $0000, $001b
dw $06a0, $07b0, $0110, $0728, $3b3b, $0000, $0000, $001c
dw $0830, $09b0, $0180, $08f0, $3c3c, $0000, $0000, $001d
dw $0e78, $0e88, $0010, $0e80, $3f3f, $0000, $0001, $001e
dw $0ee0, $0fc0, $00e0, $0f50, $3f3f, $0000, $0000, $001f
dw $0458, $0540, $00e8, $04cc, $4a4a, $0000, $0000, $0020
dw $0058, $0058, $0000, $0058, $5050, $0000, $0000, $0021
dw $0178, $0178, $0000, $0178, $5050, $0000, $0000, $0022
dw $0388, $0388, $0000, $0388, $5151, $0000, $0000, $0023
dw $0480, $05b0, $0130, $0518, $5252, $0000, $0000, $0024
dw $0f70, $0f90, $0020, $0f80, $5757, $0000, $0000, $0025
dw $0078, $0098, $0020, $0088, $5858, $0000, $0000, $0026 ;Village of Outcasts
dw $0138, $0158, $0020, $0148, $5858, $0000, $0000, $0027
dw $02e8, $0348, $0060, $0318, $5859, $0000, $0000, $0028
dw $0478, $04d0, $0058, $04a4, $5a5a, $0000, $0000, $0029
dw $0510, $0538, $0028, $0524, $5a5a, $0000, $0000, $002a
dw $0a48, $0af0, $00a8, $0a9c, $5d5d, $0000, $0000, $002b
dw $0b28, $0b38, $0010, $0b30, $5d5d, $0000, $0001, $002c
dw $0b70, $0ba0, $0030, $0b88, $5d5d, $0000, $0000, $002d
dw $0a40, $0b10, $00d0, $0aa8, $6565, $0000, $0000, $002e
dw $0350, $0390, $0040, $0370, $6969, $0000, $0000, $002f
dw $0670, $06a8, $0038, $068c, $6b6b, $0000, $0000, $0030
dw $0898, $09b0, $0118, $0924, $6c6c, $0000, $0000, $0031
dw $0a40, $0ba0, $0160, $0af0, $6d6d, $0000, $0000, $0032
dw $0c70, $0c90, $0020, $0c80, $6e6e, $0000, $0000, $0033
dw $0f70, $0f80, $0010, $0f78, $6f6f, $0000, $0000, $0034
dw $0430, $0468, $0038, $044c, $7272, $0000, $0000, $0035
dw $04d8, $04f8, $0020, $04e8, $7272, $0000, $0000, $0036
dw $0688, $06b0, $0028, $069c, $7373, $0000, $0000, $0037
dw $08d0, $08f0, $0020, $08e0, $7474, $0000, $0000, $0038
dw $0a80, $0b40, $00c0, $0ae0, $7575, $0000, $0000, $0039
dw $0d38, $0d58, $0020, $0d48, $7576, $0000, $0001, $003a
dw $0d90, $0da0, $0010, $0d98, $7576, $0000, $0000, $003b
dw $06a0, $07b0, $0110, $0728, $7b7b, $0000, $0000, $003c
dw $0830, $09b0, $0180, $08f0, $7c7c, $0000, $0000, $003d
dw $0e78, $0e88, $0010, $0e80, $7f7f, $0000, $0001, $003e
dw $0ee0, $0fc0, $00e0, $0f50, $7f7f, $0000, $0000, $003f
OWSouthEdges:
dw $0458, $0540, $00e8, $04cc, $0202, $0000, $0000, $0001
dw $0058, $0058, $0000, $0058, $0008, $0000, $0000, $0003
dw $0178, $0178, $0000, $0178, $0008, $0000, $0000, $0004
dw $0388, $0388, $0000, $0388, $0009, $0000, $0000, $0005
dw $0480, $05b0, $0130, $0518, $0a0a, $0000, $0000, $0006
dw $0f70, $0f90, $0020, $0f80, $0f0f, $0000, $0000, $0007
dw $0078, $0098, $0020, $0088, $1010, $0000, $0000, $0008
dw $0138, $0158, $0020, $0148, $1010, $0000, $0000, $0009
dw $02e8, $0348, $0060, $0318, $1111, $0000, $0000, $000a
dw $0478, $04d0, $0058, $04a4, $1212, $0000, $0000, $000b
dw $0510, $0538, $0028, $0524, $1212, $0000, $0000, $000c
dw $0a48, $0af0, $00a8, $0a9c, $1515, $0000, $0000, $000d
dw $0b28, $0b38, $0010, $0b30, $1515, $0000, $0001, $000e
dw $0b70, $0ba0, $0030, $0b88, $1515, $0000, $0000, $000f
dw $0a40, $0b10, $00d0, $0aa8, $1d1d, $0000, $0000, $0010
dw $0350, $0390, $0040, $0370, $1821, $0000, $0000, $0011
dw $0670, $06a8, $0038, $068c, $1b23, $0000, $0000, $0012
dw $0898, $09b0, $0118, $0924, $1b24, $0000, $0000, $0013
dw $0a40, $0ba0, $0160, $0af0, $2525, $0000, $0000, $0014
dw $0c70, $0c90, $0020, $0c80, $1e26, $0000, $0000, $0015
dw $0f70, $0f80, $0010, $0f78, $1e27, $0000, $0000, $0016
dw $0430, $0468, $0038, $044c, $2a2a, $0000, $0000, $0017
dw $04d8, $04f8, $0020, $04e8, $2a2a, $0000, $0000, $0018
dw $0688, $06b0, $0028, $069c, $2b2b, $0000, $0000, $0019
dw $08d0, $08f0, $0020, $08e0, $2c2c, $0000, $0000, $001a
dw $0a80, $0b40, $00c0, $0ae0, $2d2d, $0000, $0000, $001b
dw $0d38, $0d58, $0020, $0d48, $2e2e, $0000, $0001, $001c
dw $0d90, $0da0, $0010, $0d98, $2e2e, $0000, $0000, $001d
dw $06a0, $07b0, $0110, $0728, $3333, $0000, $0000, $001e
dw $0830, $09b0, $0180, $08f0, $3434, $0000, $0000, $001f
dw $0e78, $0e88, $0010, $0e80, $3737, $0000, $0001, $0020
dw $0ee0, $0fc0, $00e0, $0f50, $3737, $0000, $0000, $0021
dw $0458, $0540, $00e8, $04cc, $4242, $0000, $0000, $0022
dw $0058, $0058, $0000, $0058, $4048, $0000, $0000, $0023
dw $0178, $0178, $0000, $0178, $4048, $0000, $0000, $0024
dw $0388, $0388, $0000, $0388, $4049, $0000, $0000, $0025
dw $0480, $05b0, $0130, $0518, $4a4a, $0000, $0000, $0026
dw $0f70, $0f90, $0020, $0f80, $4f4f, $0000, $0000, $0027
dw $0078, $0098, $0020, $0088, $5050, $0000, $0000, $0028
dw $0138, $0158, $0020, $0148, $5050, $0000, $0000, $0029
dw $02e8, $0348, $0060, $0318, $5151, $0000, $0000, $002a
dw $0478, $04d0, $0058, $04a4, $5252, $0000, $0000, $002b
dw $0510, $0538, $0028, $0524, $5252, $0000, $0000, $002c
dw $0a48, $0af0, $00a8, $0a9c, $5555, $0000, $0000, $002d
dw $0b28, $0b38, $0010, $0b30, $5555, $0000, $0001, $002e
dw $0b70, $0ba0, $0030, $0b88, $5555, $0000, $0000, $002f
dw $0a40, $0b10, $00d0, $0aa8, $5d5d, $0000, $0000, $0030
dw $0350, $0390, $0040, $0370, $5861, $0000, $0000, $0031
dw $0670, $06a8, $0038, $068c, $5b63, $0000, $0000, $0032
dw $0898, $09b0, $0118, $0924, $5b64, $0000, $0000, $0033
dw $0a40, $0ba0, $0160, $0af0, $6565, $0000, $0000, $0034
dw $0c70, $0c90, $0020, $0c80, $5e66, $0000, $0000, $0035
dw $0f70, $0f80, $0010, $0f78, $5e67, $0000, $0000, $0036
dw $0430, $0468, $0038, $044c, $6a6a, $0000, $0000, $0037
dw $04d8, $04f8, $0020, $04e8, $6a6a, $0000, $0000, $0038
dw $0688, $06b0, $0028, $069c, $6b6b, $0000, $0000, $0039
dw $08d0, $08f0, $0020, $08e0, $6c6c, $0000, $0000, $003a
dw $0a80, $0b40, $00c0, $0ae0, $6d6d, $0000, $0000, $003b
dw $0d38, $0d58, $0020, $0d48, $6e6e, $0000, $0001, $003c
dw $0d90, $0da0, $0010, $0d98, $6e6e, $0000, $0000, $003d
dw $06a0, $07b0, $0110, $0728, $7373, $0000, $0000, $003e
dw $0830, $09b0, $0180, $08f0, $7474, $0000, $0000, $003f
dw $0e78, $0e88, $0010, $0e80, $7777, $0000, $0001, $0040
dw $0ee0, $0fc0, $00e0, $0f50, $7777, $0000, $0000, $0041
dw $0080, $0080, $0000, $0080, $8080, $0000, $0000, $0000 ;Pedestal (unused)
dw $0288, $02c0, $0038, $02a4, $8189, $0000, $0000, $0002 ;Zora (unused)
OWWestEdges:
dw $0070, $00a0, $0030, $0088, $0202, $0000, $0000, $0000
dw $0068, $0078, $0010, $0070, $0505, $0000, $0000, $0001
dw $0068, $0088, $0020, $0078, $0707, $0000, $0000, $0002
dw $0318, $0368, $0050, $0340, $050d, $0000, $0000, $0003
dw $0450, $0488, $0038, $046c, $1212, $0000, $0000, $0004
dw $0560, $05a0, $0040, $0580, $1212, $0000, $0000, $0005
dw $0488, $0500, $0078, $04c4, $1313, $0000, $0000, $0006
dw $0538, $05a8, $0070, $0570, $1313, $0000, $0000, $0007
dw $0470, $05a8, $0138, $050c, $1414, $0000, $0000, $0008
dw $0470, $0598, $0128, $0504, $1515, $0000, $0000, $0009
dw $0480, $0488, $0008, $0484, $1616, $0000, $0001, $000a
dw $04b0, $0510, $0060, $04e0, $1616, $0000, $0000, $000b
dw $0560, $0588, $0028, $0574, $1616, $0000, $0000, $000c
dw $0450, $0458, $0008, $0454, $1717, $0000, $0001, $000d
dw $0480, $04a8, $0028, $0494, $1717, $0000, $0000, $000e
dw $0718, $0738, $0020, $0728, $1b1b, $0000, $0000, $000f
dw $0908, $0948, $0040, $0928, $2222, $0000, $0000, $0010
dw $0878, $08a8, $0030, $0890, $2525, $0000, $0000, $0011
dw $0bb8, $0bc8, $0010, $0bc0, $2929, $0000, $0000, $0012
dw $0b60, $0ba0, $0040, $0b80, $2a2a, $0000, $0000, $0013
dw $0ab0, $0ad0, $0020, $0ac0, $2c2c, $0000, $0000, $0014
dw $0af0, $0b40, $0050, $0b18, $2c2c, $0000, $0000, $0015
dw $0b78, $0ba0, $0028, $0b8c, $2c2c, $0000, $0000, $0016
dw $0b10, $0b28, $0018, $0b1c, $2d2d, $0000, $0001, $604a ;Stone Bridge (exit only)
dw $0b68, $0b98, $0030, $0b80, $2d2d, $0000, $0000, $0017
dw $0a68, $0ab8, $0050, $0a90, $2e2e, $0000, $0000, $0018
dw $0b00, $0b78, $0078, $0b3c, $2e2e, $0000, $0001, $0019
dw $0c50, $0db8, $0168, $0d04, $3333, $0000, $0000, $001a
dw $0c78, $0ce3, $006b, $0cad, $3434, $0000, $0000, $001b
dw $0ce4, $0d33, $004f, $0d0b, $3434, $0000, $0001, $001c
dw $0d34, $0db8, $0084, $0d76, $3434, $0000, $0000, $001d
dw $0ea8, $0f20, $0078, $0ee4, $3a3a, $0000, $0000, $001e
dw $0f70, $0fa8, $0038, $0f8c, $3a3a, $0000, $0000, $001f
dw $0f18, $0f18, $0000, $0f18, $3b3b, $0000, $0000, $0020
dw $0fc8, $0fc8, $0000, $0fc8, $3b3b, $0000, $0000, $0021
dw $0e28, $0fb8, $0190, $0ef0, $3c3c, $0000, $0000, $0022
dw $0f78, $0fb8, $0040, $0f98, $353d, $0000, $0000, $0023
dw $0f20, $0f40, $0020, $0f30, $3f3f, $0000, $0001, $0024
dw $0f70, $0fb8, $0048, $0f94, $3f3f, $0000, $0000, $0025
dw $0070, $00a0, $0030, $0088, $4242, $0000, $0000, $0026
dw $0068, $0078, $0010, $0070, $4545, $0000, $0000, $0027
dw $0068, $0088, $0020, $0078, $4747, $0000, $0000, $0028
dw $0318, $0368, $0050, $0340, $454d, $0000, $0000, $0029
dw $0450, $0488, $0038, $046c, $5252, $0000, $0000, $002a
dw $0560, $05a0, $0040, $0580, $5252, $0000, $0000, $002b
dw $0488, $0500, $0078, $04c4, $5353, $0000, $0000, $002c
dw $0538, $05a8, $0070, $0570, $5353, $0000, $0000, $002d
dw $0470, $05a8, $0138, $050c, $5454, $0000, $0000, $002e
dw $0470, $0598, $0128, $0504, $5555, $0000, $0000, $002f
dw $0480, $0488, $0008, $0484, $5656, $0000, $0001, $0030
dw $04b0, $0510, $0060, $04e0, $5656, $0000, $0000, $0031
dw $0560, $0588, $0028, $0574, $5656, $0000, $0000, $0032
dw $0450, $0458, $0008, $0454, $5757, $0000, $0001, $0033
dw $0480, $04a8, $0028, $0494, $5757, $0000, $0000, $0034
dw $0908, $0948, $0040, $0928, $6262, $0000, $0000, $0035
dw $0878, $08a8, $0030, $0890, $6565, $0000, $0000, $0036
dw $0b60, $0b68, $0008, $0b64, $6969, $0000, $0000, $0037
dw $0bb8, $0bc8, $0010, $0bc0, $6969, $0000, $0000, $0038
dw $0b60, $0ba0, $0040, $0b80, $6a6a, $0000, $0000, $0039
dw $0ab0, $0ad0, $0020, $0ac0, $6c6c, $0000, $0000, $003a
dw $0af0, $0b40, $0050, $0b18, $6c6c, $0000, $0000, $003b
dw $0b78, $0ba0, $0028, $0b8c, $6c6c, $0000, $0000, $003c
dw $0b68, $0b98, $0030, $0b80, $6d6d, $0000, $0000, $003d
dw $0a68, $0ab8, $0050, $0a90, $6e6e, $0000, $0000, $003e
dw $0b00, $0b78, $0078, $0b3c, $6e6e, $0000, $0001, $003f
dw $0c50, $0db8, $0168, $0d04, $7373, $0000, $0000, $0040
dw $0c78, $0ce3, $006b, $0cad, $7474, $0000, $0000, $0041
dw $0ce4, $0d33, $004f, $0d0b, $7474, $0000, $0001, $0042
dw $0d34, $0db8, $0084, $0d76, $7474, $0000, $0000, $0043
dw $0f18, $0f18, $0000, $0f18, $7b7b, $0000, $0000, $0044
dw $0fc8, $0fc8, $0000, $0fc8, $7b7b, $0000, $0000, $0045
dw $0e28, $0fb8, $0190, $0ef0, $7c7c, $0000, $0000, $0046
dw $0f78, $0fb8, $0040, $0f98, $757d, $0000, $0000, $0047
dw $0f20, $0f40, $0020, $0f30, $7f7f, $0000, $0001, $0048
dw $0f70, $0fb8, $0048, $0f94, $7f7f, $0000, $0000, $0049
OWEastEdges:
dw $0070, $00a0, $0030, $0088, $0001, $0000, $0000, $0000
dw $0068, $0078, $0010, $0070, $0304, $0000, $0000, $0001
dw $0068, $0088, $0020, $0078, $0506, $0000, $0000, $0002
dw $0318, $0368, $0050, $0340, $030c, $0000, $0000, $0003
dw $0450, $0488, $0038, $046c, $1111, $0000, $0000, $0004
dw $0560, $05a0, $0040, $0580, $1111, $0000, $0000, $0005
dw $0488, $0500, $0078, $04c4, $1212, $0000, $0000, $0006
dw $0538, $05a8, $0070, $0570, $1212, $0000, $0000, $0007
dw $0470, $05a8, $0138, $050c, $1313, $0000, $0000, $0008
dw $0470, $0598, $0128, $0504, $1414, $0000, $0000, $0009
dw $0480, $0488, $0008, $0484, $1515, $0000, $0001, $000a
dw $04b0, $0510, $0060, $04e0, $1515, $0000, $0000, $000b
dw $0560, $0588, $0028, $0574, $1515, $0000, $0000, $000c
dw $0450, $0458, $0008, $0454, $1616, $0000, $0001, $000d
dw $0480, $04a8, $0028, $0494, $1616, $0000, $0000, $000e
dw $0718, $0738, $0020, $0728, $1a1a, $0000, $0000, $000f
dw $0908, $0948, $0040, $0928, $1821, $0000, $0000, $0010
dw $0878, $08a8, $0030, $0890, $1b24, $0000, $0000, $0011
dw $0bb8, $0bc8, $0010, $0bc0, $2828, $0000, $0000, $0012 ;Race Game
dw $0b60, $0ba0, $0040, $0b80, $2929, $0000, $0000, $0013
dw $0ab0, $0ad0, $0020, $0ac0, $2b2b, $0000, $0000, $0014
dw $0af0, $0b40, $0050, $0b18, $2b2b, $0000, $0000, $0015
dw $0b78, $0ba0, $0028, $0b8c, $2b2b, $0000, $0000, $0016
dw $0b68, $0b98, $0030, $0b80, $2c2c, $0000, $0000, $0018
dw $0a68, $0ab8, $0050, $0a90, $2d2d, $0000, $0000, $0019
dw $0b00, $0b78, $0078, $0b3c, $2d2d, $0000, $0001, $001a
dw $0c50, $0db8, $0168, $0d04, $3232, $0000, $0000, $001b
dw $0c78, $0ce3, $006b, $0cad, $3333, $0000, $0000, $001c
dw $0ce4, $0d33, $004f, $0d0b, $3333, $0000, $0001, $001d
dw $0d34, $0db8, $0084, $0d76, $3333, $0000, $0000, $001e
dw $0ea8, $0f20, $0078, $0ee4, $3039, $0000, $0000, $001f
dw $0f70, $0fa8, $0038, $0f8c, $3039, $0000, $0000, $0020
dw $0f18, $0f18, $0000, $0f18, $3a3a, $0000, $0000, $0021
dw $0fc8, $0fc8, $0000, $0fc8, $3a3a, $0000, $0000, $0022
dw $0e28, $0fb8, $0190, $0ef0, $3b3b, $0000, $0000, $0023
dw $0f78, $0fb8, $0040, $0f98, $3c3c, $0000, $0000, $0024
dw $0f20, $0f40, $0020, $0f30, $353e, $0000, $0001, $0025
dw $0f70, $0fb8, $0048, $0f94, $353e, $0000, $0000, $0026
dw $0070, $00a0, $0030, $0088, $4041, $0000, $0000, $0027 ;Skull Woods
dw $0068, $0078, $0010, $0070, $4344, $0000, $0000, $0028
dw $0068, $0088, $0020, $0078, $4546, $0000, $0000, $0029
dw $0318, $0368, $0050, $0340, $434c, $0000, $0000, $002a
dw $0450, $0488, $0038, $046c, $5151, $0000, $0000, $002b
dw $0560, $05a0, $0040, $0580, $5151, $0000, $0000, $002c
dw $0488, $0500, $0078, $04c4, $5252, $0000, $0000, $002d
dw $0538, $05a8, $0070, $0570, $5252, $0000, $0000, $002e
dw $0470, $05a8, $0138, $050c, $5353, $0000, $0000, $002f
dw $0470, $0598, $0128, $0504, $5454, $0000, $0000, $0030
dw $0480, $0488, $0008, $0484, $5555, $0000, $0001, $0031
dw $04b0, $0510, $0060, $04e0, $5555, $0000, $0000, $0032
dw $0560, $0588, $0028, $0574, $5555, $0000, $0000, $0033
dw $0450, $0458, $0008, $0454, $5656, $0000, $0001, $0034
dw $0480, $04a8, $0028, $0494, $5656, $0000, $0000, $0035
dw $0908, $0948, $0040, $0928, $5861, $0000, $0000, $0036
dw $0878, $08a8, $0030, $0890, $5b64, $0000, $0000, $0037
dw $0b60, $0b68, $0008, $0b64, $6868, $0000, $0000, $0038 ;Dig Game
dw $0bb8, $0bc8, $0010, $0bc0, $6868, $0000, $0000, $0039
dw $0b60, $0ba0, $0040, $0b80, $6969, $0000, $0000, $003a
dw $0ab0, $0ad0, $0020, $0ac0, $6b6b, $0000, $0000, $003b
dw $0af0, $0b40, $0050, $0b18, $6b6b, $0000, $0000, $003c
dw $0b78, $0ba0, $0028, $0b8c, $6b6b, $0000, $0000, $003d
dw $0b68, $0b98, $0030, $0b80, $6c6c, $0000, $0000, $003e
dw $0a68, $0ab8, $0050, $0a90, $6d6d, $0000, $0000, $003f
dw $0b00, $0b78, $0078, $0b3c, $6d6d, $0000, $0001, $0040
dw $0c50, $0db8, $0168, $0d04, $7272, $0000, $0000, $0041
dw $0c78, $0ce3, $006b, $0cad, $7373, $0000, $0000, $0042
dw $0ce4, $0d33, $004f, $0d0b, $7373, $0000, $0001, $0043
dw $0d34, $0db8, $0084, $0d76, $7373, $0000, $0000, $0044
dw $0f18, $0f18, $0000, $0f18, $7a7a, $0000, $0000, $0045
dw $0fc8, $0fc8, $0000, $0fc8, $7a7a, $0000, $0000, $0046
dw $0e28, $0fb8, $0190, $0ef0, $7b7b, $0000, $0000, $0047
dw $0f78, $0fb8, $0040, $0f98, $7c7c, $0000, $0000, $0048
dw $0f20, $0f40, $0020, $0f30, $757e, $0000, $0001, $0049
dw $0f70, $0fb8, $0048, $0f94, $757e, $0000, $0000, $004a
dw $0058, $00c0, $0068, $008c, $8080, $0000, $0001, $0017 ;Hobo (unused)

org $aab9a0 ;PC 1539a0
OWSpecialDestIndex:
dw $0080, $0081, $0082

org $aab9b0 ;PC 1539b0
OWTileWorldAssoc:
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $40, $40, $40, $40, $40, $40, $40, $40
db $00, $00

org $aaba70 ;PC 153a70
OWTileMapAlt:
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0

db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0
db 0, 0, 0, 0, 0, 0, 0, 0

db 0, 0

;================================================================================
; Bonk Prize Data ($AABB00 - $AABBFB)
;--------------------------------------------------------------------------------
; This table stores data relating to bonk locations for Bonk Drop Shuffle
; 
; Example: We can use OWBonkPrizeTable[$09].loot to read what item is in the
; east tree on the Sanctuary screen
;--------------------------------------------------------------------------------
; Search Criteria - The following two fields are used as a unique index
; .owid         = OW screen ID 
; .yx           = Y & X coordinate data *see below*
; 
; .flag         = OW event flag bitmask
; .loot         = Loot ID
; .mw_player    = Multiworld player ID
; .vert_offset  = Vertical offset, # of pixels the sprite moves up when activated
;
; .yx field is a combination of both the least significant digits of the Y and X
; coordinates of the static location of the sprite located in a bonk location.
; All sprites, when initialized, are aligned by a 16 pixel increment.
; The coordinate system in LTTP is handled by two bytes:
;        (high)             (low)
;   - - - w  w w w s   s s s s  s s s s
;   w = world absolute coords, every screen is $200 pixels in each dimension
;   s = local screen coords, coords relative to the bounds of the current screen
; Because of the 16 pixel alignment of sprites, the last four bits of the coords
; are unset. This leaves 5 bits remaining, we simply disregard the highest bit
; and then combine the Y and X coords together to be used as search criteria.
; This does open the possibility of a false positive match from 3 other coords
; on the same screen (15 on megatile screens) but there are no bonk sprites that
; have collision in this regard.
;--------------------------------------------------------------------------------
struct OWBonkPrizeTable $AABB00
    .owid: skip 1
    .yx: skip 1
    .flag: skip 1
    .loot: skip 1
    .mw_player: skip 1
    .vert_offset: skip 1
endstruct align 6

org $aabb00 ;PC 153b00
OWBonkPrizeData:
; OWID  YX  Flag  Item  MW Offset
db $00, $59, $10, $b0, $00, $20
db $05, $04, $10, $b2, $00, $00
db $0a, $4e, $10, $b0, $00, $20
db $0a, $a9, $08, $b1, $00, $20
db $10, $c7, $10, $b1, $00, $20
db $10, $f7, $08, $b4, $00, $20
db $11, $08, $10, $27, $00, $00
db $12, $a4, $10, $b2, $00, $20
db $13, $c7, $10, $31, $00, $20
db $13, $98, $08, $b1, $00, $20
db $15, $a4, $10, $b1, $00, $20
db $15, $fb, $08, $b2, $00, $20
db $18, $a8, $10, $b2, $00, $20
db $18, $36, $08, $35, $00, $20
db $1a, $8a, $10, $42, $00, $20
db $1a, $1d, $08, $b2, $00, $20
db $ff, $77, $04, $35, $00, $20  ; pre aga ONLY ; hijacked murahdahla bonk tree
db $1b, $46, $10, $b1, $00, $10
db $1d, $6b, $10, $b1, $00, $20
db $1e, $72, $10, $b2, $00, $20
db $2a, $8f, $10, $36, $00, $20
db $2a, $45, $08, $36, $00, $20
db $2b, $d6, $10, $b2, $00, $20
db $2e, $9c, $10, $b2, $00, $20
db $2e, $b4, $08, $b0, $00, $20
db $32, $29, $10, $42, $00, $20
db $32, $9a, $08, $b2, $00, $20
db $42, $66, $10, $b2, $00, $20
db $51, $08, $10, $b2, $00, $04
db $51, $09, $08, $b2, $00, $04
db $54, $b5, $10, $27, $00, $14
db $54, $ef, $08, $b2, $00, $08
db $54, $b9, $04, $36, $00, $00
db $55, $aa, $10, $b0, $00, $20
db $55, $fb, $08, $35, $00, $20
db $56, $e4, $10, $b0, $00, $20
db $5b, $a7, $10, $b2, $00, $20
db $5e, $00, $10, $b2, $00, $20
db $6e, $8c, $10, $35, $00, $10
db $6e, $90, $08, $b0, $00, $10
db $6e, $a4, $04, $b1, $00, $10
db $74, $4e, $10, $b1, $00, $1c

; temporary fix - murahdahla replaces one of the bonk tree prizes
;    so we copy the sprite table here and update the pointer
;    longterm solution should be to spawn in murahdahla separately
org $09AE2A
Overworld_Sprites_Screen1A_2:
db $08, $0F, $41 ; yx:{ 0x080, 0x0F0 }
db $0E, $0C, $41 ; yx:{ 0x0E0, 0x0C0 }
db $11, $0D, $E3 ; yx:{ 0x110, 0x0D0 }
db $18, $0A, $D8 ; yx:{ 0x180, 0x0A0 }
db $18, $0F, $45 ; yx:{ 0x180, 0x0F0 }
db $FF ; END
org $09CA55
dw Overworld_Sprites_Screen1A_2&$FFFF