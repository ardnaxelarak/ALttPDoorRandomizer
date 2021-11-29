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
org $02a999
jsl OWEdgeTransition : nop #4 ;LDA $02A4E3,X : ORA $7EF3CA
;org $02e238 ;LDX #$9E : - DEX : DEX : CMP $DAEE,X : BNE -
;jsl OWSpecialTransition : nop #5

org $05af75
jsl OWPreserveMirrorSprite : nop #2 ; LDA $7EF3CA : BNE $05AFDF

; whirlpool shuffle cross world change
org $02b3bd
jsl OWWhirlpoolUpdate ;JSL $02EA6C

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

;(replacing -> LDA $8A : AND.b #$40)
org $00d8c4  ; < ? - Bank00.asm:4068 ()
jsl.l OWWorldCheck
org $0283dc  ; < ? - Bank02.asm:816 ()
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
org $0aba6c  ; < ? - Bank0a.asm:474 ()
jsl.l OWWorldCheck16 : nop
org $0aba99  ; < ? - Bank0a.asm:515 ()
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
and #$7f : eor #$40 : nop #2 ; something to do with mirroring and simply toggling world to opposite one: TODO: better comment

;Code
org $aa8800
OWCoordIndex: ; Horizontal 1st
db 2, 2, 0, 0 ; Coordinate Index $20-$23
OWOppCoordIndex: ; Horizontal 1st
db 0, 0, 2, 2 ; Coordinate Index $20-$23
OWBGIndex: ; Horizontal 1st
db 0, 0, 6, 6 ; BG Scroll Index $e2-$ea
OWOppBGIndex: ; Horizontal 1st
db 6, 6, 0, 0 ; BG Scroll Index $e2-$ea
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

OWWhirlpoolUpdate:
{
    jsl $02ea6c ; what we wrote over
    lda.l OWFlags : and #$01 : bne +
    lda.l OWMode+1 : and #$02 : beq .return
        + ldx $8a : jsr OWWorldUpdate
    .return
    rtl
}

OWPreserveMirrorSprite:
{
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq .vanilla
        rtl ; if OW Crossed, skip world check and continue
    .vanilla
    lda $7ef3ca : bne .deleteMirror
        rtl

    .deleteMirror
    pla : lda #$de : pha ; in vanilla, if in dark world, jump to $05afdf
    rtl
}

OWFluteCancel:
{
    lda.l OWFlags+1 : and #$01 : bne +
        jsl $02e99d : rtl
    + lda $7f5006 : cmp #$01 : beq +
        jsl $02e99d
    + lda #$00 : sta $7f5006 : rtl
}
OWFluteCancel2:
{
    lda $f2 : ora $f0 : and #$c0 : bne +
        jml $0ab7bd
    + inc $0200
    lda.l OWFlags+1 : and #$01 : beq +
    lda $f2 : cmp #$40 : bne +
        lda #$01 : sta $7f5006
    + rtl 
}
OWSmithAccept:
{
    lda $7ef3cc : cmp #$07 : beq +
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

org $aa9000
OWEdgeTransition:
{
    php : phy
    lda.l OWMode : ora.l OWMode+1 : beq +
        jsl OWShuffle : bra .return
    + jsl OWVanilla
    .return
    ply : plp : rtl
}
OWVanilla:
{
    lda $02a4e3,X : ora $7ef3ca : rtl
}
OWShuffle:
{
    ;Assume you're at links house = $2c
    ;transitioning right will result in X = $2d
    ;transitioning left will result in X = $2b
    ;up X = $24
    ;down X = $34

    ;compares X to determine direction of edge transition
    phx : lsr $700 : cpx $700 : !blt .upOrLeft
        dex : cpx $700 : bne .downEdge
            lda #$3 : sta $418 : bra .setOWID ;right
        .downEdge
            lda #$1 : sta $418 : bra .setOWID ;down
    .upOrLeft
        inx : cpx $700 : bne .upEdge
                lda #$2 : sta $418 : bra .setOWID ;left
            .upEdge
                lda #$0 : sta $418 ;up

    .setOWID
    ;look up transitions in current area in table OWEdgeOffsets
    ;offset is (8bytes * OW Slot ID) + (2bytes * direction)
    asl : rep #$20 : pha : sep #$20 ;2 bytes per direction
    lda $8a : and #$40 : !add $700 : rep #$30 : and #$00ff : asl #3
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
        jsr OWSearchTransition : bcs .newDestination
        txa : !add #$0010 : tax
    pla : dec : bne .nextTransition : bra .noTransition

    .newDestination
    pla : sep #$30 : plx : lda $8a : bra .return

    .noTransition
    sep #$30 : plx : jsl OWVanilla

    .return
    rtl
}
OWSearchTransition:
{
    ;A-16 XY-16
    lda $418 : bne + ;north
        lda.l OWNorthEdges,x : dec
        cmp $22 : !bge .nomatch
        lda.l OWNorthEdges+2,x : cmp $22 : !blt .nomatch
            ;MATCH
            lda.l OWNorthEdges+14,x : tay ;y = record id of dest
            sep #$20 : lda #OWSouthEdges>>16 : phb : pha : plb
                ldx #OWSouthEdges : jsr OWNewDestination : plb ;x = address of table
            bra .matchfound
    + dec : bne + ;south
        lda.l OWSouthEdges,x : dec
        cmp $22 : !bge .exitloop
        lda.l OWSouthEdges+2,x : cmp $22 : !blt .exitloop
            ;MATCH
            lda.l OWSouthEdges+14,x : tay ;y = record id of dest
            sep #$20 : lda #OWNorthEdges>>16 : phb : pha : plb : phx
                ldx #OWNorthEdges : jsr OWNewDestination : plx : plb ;x = address of table
            bra .matchfound
        .nomatch
            bra .exitloop
    + dec : bne + ; west
        lda.l OWWestEdges,x : dec
        cmp $20 : !bge .exitloop
        lda.l OWWestEdges+2,x : cmp $20 : !blt .exitloop
            ;MATCH
            lda.l OWWestEdges+14,x : tay ;y = record id of dest
            sep #$20 : lda #OWEastEdges>>16 : phb : pha : plb
                ldx #OWEastEdges : jsr OWNewDestination : plb ;x = address of table
            bra .matchfound
    + lda.l OWEastEdges,x : dec ;east
        cmp $20 : !bge .exitloop
        lda.l OWEastEdges+2,x : cmp $20 : !blt .exitloop
            ;MATCH
            lda.l OWEastEdges+14,x : tay ;y = record id of dest
            sep #$20 : lda #OWWestEdges>>16 : phb : pha : plb
                ldx #OWWestEdges : jsr OWNewDestination : plb ;x = address of table

    .matchfound
    plx : pla : pea $0001 : phx
    sec : rts

    .exitloop
    clc : rts
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
    ;LDA $84 : SEC : SBC #$0400 : AND #$0F80 : ASL : XBA : STA $88 ; vram
    LDA $84 : SEC : SBC #$0400 : AND #$0F00 : ASL : XBA : STA $88
    LDA $84 : SEC : SBC #$0010 : AND #$003E : LSR : STA $86

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

    sep #$30 : lda OWOppSlotOffset,y : !add $04 : asl : and #$7f : sta $700
    
    ; crossed OW shuffle
    lda.l OWMode+1 : and.b #!FLAG_OW_CROSSED : beq .return
        ldx $05 : jsr OWWorldUpdate

    .return
    lda $05 : sta $8a
    ;bra +
    ;    nop #8
    ;    jsl $02EA41
    ;    nop #8
    ;+
    rep #$30 : rts
}
OWWorldUpdate: ; x = owid of destination screen
{
    lda.l OWTileWorldAssoc,x : cmp.l $7ef3ca : beq .return
        sta.l $7ef3ca ; change world
        lda #$38 : sta $012f ; play sfx - #$3b is an alternative

        ; toggle bunny mode
        lda $7ef357 : bne .nobunny
        lda.l InvertedMode : bne .inverted
            lda $7ef3ca : and.b #$40 : bra +
            .inverted lda $7ef3ca : and.b #$40 : eor #$40
        + cmp #$40 : bne .nobunny
            ; turn into bunny
            lda $5d : cmp #$04 : beq + ; if swimming, continue
                lda #$17 : sta $5d
            + lda #$01 : sta $02e0 : sta $56
            bra .return

        .nobunny
        lda $5d : cmp #$17 : bne + ; retain current state unless bunny
            stz $5d
        + stz $02e0 : stz $56

    .return
    rts
}
OWSpecialTransition:
{
    LDX #$9E
    - DEX : DEX : CMP $DAEE,X : BNE -
}

;Data
org $aaa000
OWEdgeOffsets:
;2 bytes per each direction per each OW Slot, order is NSWE per value at $0418
;AABB, A = offset to the transition table, B = number of transitions
dw $0001, $0000, $0000, $0000 ;OW Slot 00, OWID 0x00 Lost Woods
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
dw $0201, $0501, $0000, $0000 ;Zora

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
dw $1401, $1901, $1702, $1802 ;Hobo
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

org $aaa800 ;PC 152800
OWNorthEdges:
;   Min    Max   Width   Mid OW Slot/OWID VRAM *FREE* Dest Index
dw $00a0, $00a0, $0000, $00a0, $0000, $0000, $0000, $0040 ;Lost Woods
dw $0458, $0540, $00e8, $04cc, $0a0a, $0000, $0000, $0000
dw $0f38, $0f60, $0028, $0f4c, $0f0f, $0000, $0000, $0041
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
dw $0b28, $0b38, $0010, $0b30, $1d1d, $0000, $0000, $000c
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
dw $0d38, $0d58, $0020, $0d48, $3536, $0000, $0000, $001a
dw $0d90, $0da0, $0010, $0d98, $3536, $0000, $0000, $001b
dw $06a0, $07b0, $0110, $0728, $3b3b, $0000, $0000, $001c
dw $0830, $09b0, $0180, $08f0, $3c3c, $0000, $0000, $001d
dw $0e78, $0e88, $0010, $0e80, $3f3f, $0000, $0000, $001e
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
dw $0b28, $0b38, $0010, $0b30, $5d5d, $0000, $0000, $002c
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
dw $0d38, $0d58, $0020, $0d48, $7576, $0000, $0000, $003a
dw $0d90, $0da0, $0010, $0d98, $7576, $0000, $0000, $003b
dw $06a0, $07b0, $0110, $0728, $7b7b, $0000, $0000, $003c
dw $0830, $09b0, $0180, $08f0, $7c7c, $0000, $0000, $003d
dw $0e78, $0e88, $0010, $0e80, $7f7f, $0000, $0000, $003e
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
dw $0b28, $0b38, $0010, $0b30, $1515, $0000, $0000, $000e
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
dw $0d38, $0d58, $0020, $0d48, $2e2e, $0000, $0000, $001c
dw $0d90, $0da0, $0010, $0d98, $2e2e, $0000, $0000, $001d
dw $06a0, $07b0, $0110, $0728, $3333, $0000, $0000, $001e
dw $0830, $09b0, $0180, $08f0, $3434, $0000, $0000, $001f
dw $0e78, $0e88, $0010, $0e80, $3737, $0000, $0000, $0020
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
dw $0b28, $0b38, $0010, $0b30, $5555, $0000, $0000, $002e
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
dw $0d38, $0d58, $0020, $0d48, $6e6e, $0000, $0000, $003c
dw $0d90, $0da0, $0010, $0d98, $6e6e, $0000, $0000, $003d
dw $06a0, $07b0, $0110, $0728, $7373, $0000, $0000, $003e
dw $0830, $09b0, $0180, $08f0, $7474, $0000, $0000, $003f
dw $0e78, $0e88, $0010, $0e80, $7777, $0000, $0000, $0040
dw $0ee0, $0fc0, $00e0, $0f50, $7777, $0000, $0000, $0041
dw $0080, $0080, $0000, $0080, $8080, $0000, $0000, $0000 ;Pedestal
dw $0288, $02c0, $0038, $02a4, $8189, $0000, $0000, $0002 ;Zora
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
dw $0480, $0488, $0008, $0484, $1616, $0000, $0000, $000a
dw $04b0, $0510, $0060, $04e0, $1616, $0000, $0000, $000b
dw $0560, $0588, $0028, $0574, $1616, $0000, $0000, $000c
dw $0450, $0458, $0008, $0454, $1717, $0000, $0000, $000d
dw $0480, $04a8, $0028, $0494, $1717, $0000, $0000, $000e
dw $0718, $0738, $0020, $0728, $1b1b, $0000, $0000, $000f
dw $0908, $0948, $0040, $0928, $2222, $0000, $0000, $0010
dw $0878, $08a8, $0030, $0890, $2525, $0000, $0000, $0011
dw $0bb8, $0bc8, $0010, $0bc0, $2929, $0000, $0000, $0012
dw $0b60, $0ba0, $0040, $0b80, $2a2a, $0000, $0000, $0013
dw $0ab0, $0ad0, $0020, $0ac0, $2c2c, $0000, $0000, $0014
dw $0af0, $0b40, $0050, $0b18, $2c2c, $0000, $0000, $0015
dw $0b78, $0ba0, $0028, $0b8c, $2c2c, $0000, $0000, $0016
dw $0b10, $0b28, $0018, $0b1c, $2d2d, $0000, $0000, $004a
dw $0b68, $0b98, $0030, $0b80, $2d2d, $0000, $0000, $0017
dw $0a68, $0ab8, $0050, $0a90, $2e2e, $0000, $0000, $0018
dw $0b00, $0b78, $0078, $0b3c, $2e2e, $0000, $0000, $0019
dw $0c50, $0db8, $0168, $0d04, $3333, $0000, $0000, $001a
dw $0c78, $0ce3, $006b, $0cad, $3434, $0000, $0000, $001b
dw $0ce4, $0d33, $004f, $0d0b, $3434, $0000, $0000, $001c
dw $0d34, $0db8, $0084, $0d76, $3434, $0000, $0000, $001d
dw $0ea8, $0f20, $0078, $0ee4, $3a3a, $0000, $0000, $001e
dw $0f70, $0fa8, $0038, $0f8c, $3a3a, $0000, $0000, $001f
dw $0f18, $0f18, $0000, $0f18, $3b3b, $0000, $0000, $0020
dw $0fc8, $0fc8, $0000, $0fc8, $3b3b, $0000, $0000, $0021
dw $0e28, $0fb8, $0190, $0ef0, $3c3c, $0000, $0000, $0022
dw $0f78, $0fb8, $0040, $0f98, $353d, $0000, $0000, $0023
dw $0f20, $0f40, $0020, $0f30, $3f3f, $0000, $0000, $0024
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
dw $0480, $0488, $0008, $0484, $5656, $0000, $0000, $0030
dw $04b0, $0510, $0060, $04e0, $5656, $0000, $0000, $0031
dw $0560, $0588, $0028, $0574, $5656, $0000, $0000, $0032
dw $0450, $0458, $0008, $0454, $5757, $0000, $0000, $0033
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
dw $0b00, $0b78, $0078, $0b3c, $6e6e, $0000, $0000, $003f
dw $0c50, $0db8, $0168, $0d04, $7373, $0000, $0000, $0040
dw $0c78, $0ce3, $006b, $0cad, $7474, $0000, $0000, $0041
dw $0ce4, $0d33, $004f, $0d0b, $7474, $0000, $0000, $0042
dw $0d34, $0db8, $0084, $0d76, $7474, $0000, $0000, $0043
dw $0f18, $0f18, $0000, $0f18, $7b7b, $0000, $0000, $0044
dw $0fc8, $0fc8, $0000, $0fc8, $7b7b, $0000, $0000, $0045
dw $0e28, $0fb8, $0190, $0ef0, $7c7c, $0000, $0000, $0046
dw $0f78, $0fb8, $0040, $0f98, $757d, $0000, $0000, $0047
dw $0f20, $0f40, $0020, $0f30, $7f7f, $0000, $0000, $0048
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
dw $0480, $0488, $0008, $0484, $1515, $0000, $0000, $000a
dw $04b0, $0510, $0060, $04e0, $1515, $0000, $0000, $000b
dw $0560, $0588, $0028, $0574, $1515, $0000, $0000, $000c
dw $0450, $0458, $0008, $0454, $1616, $0000, $0000, $000d
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
dw $0b00, $0b78, $0078, $0b3c, $2d2d, $0000, $0000, $001a
dw $0c50, $0db8, $0168, $0d04, $3232, $0000, $0000, $001b
dw $0c78, $0ce3, $006b, $0cad, $3333, $0000, $0000, $001c
dw $0ce4, $0d33, $004f, $0d0b, $3333, $0000, $0000, $001d
dw $0d34, $0db8, $0084, $0d76, $3333, $0000, $0000, $001e
dw $0ea8, $0f20, $0078, $0ee4, $3039, $0000, $0000, $001f
dw $0f70, $0fa8, $0038, $0f8c, $3039, $0000, $0000, $0020
dw $0f18, $0f18, $0000, $0f18, $3a3a, $0000, $0000, $0021
dw $0fc8, $0fc8, $0000, $0fc8, $3a3a, $0000, $0000, $0022
dw $0e28, $0fb8, $0190, $0ef0, $3b3b, $0000, $0000, $0023
dw $0f78, $0fb8, $0040, $0f98, $3c3c, $0000, $0000, $0024
dw $0f20, $0f40, $0020, $0f30, $353e, $0000, $0000, $0025
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
dw $0480, $0488, $0008, $0484, $5555, $0000, $0000, $0031
dw $04b0, $0510, $0060, $04e0, $5555, $0000, $0000, $0032
dw $0560, $0588, $0028, $0574, $5555, $0000, $0000, $0033
dw $0450, $0458, $0008, $0454, $5656, $0000, $0000, $0034
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
dw $0b00, $0b78, $0078, $0b3c, $6d6d, $0000, $0000, $0040
dw $0c50, $0db8, $0168, $0d04, $7272, $0000, $0000, $0041
dw $0c78, $0ce3, $006b, $0cad, $7373, $0000, $0000, $0042
dw $0ce4, $0d33, $004f, $0d0b, $7373, $0000, $0000, $0043
dw $0d34, $0db8, $0084, $0d76, $7373, $0000, $0000, $0044
dw $0f18, $0f18, $0000, $0f18, $7a7a, $0000, $0000, $0045
dw $0fc8, $0fc8, $0000, $0fc8, $7a7a, $0000, $0000, $0046
dw $0e28, $0fb8, $0190, $0ef0, $7b7b, $0000, $0000, $0047
dw $0f78, $0fb8, $0040, $0f98, $7c7c, $0000, $0000, $0048
dw $0f20, $0f40, $0020, $0f30, $757e, $0000, $0000, $0049
dw $0f70, $0fb8, $0048, $0f94, $757e, $0000, $0000, $004a
dw $0058, $00c0, $0068, $008c, $8080, $0000, $0000, $0017 ;Hobo

org $aaba00 ;PC 153a00
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

org $aabb00 ;PC 153b00
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
