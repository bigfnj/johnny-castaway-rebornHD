#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ads.h"
#include "art_style.h"
#include "events.h"
#include "graphics.h"
#include "island.h"
#include "resource.h"
#include "sound.h"
#include "utils.h"
#include "zipvfs.h"
#include "ttm.h"

static int enabled, ticks, displays, pending, frame_no, flip_no, px,py,pw,ph,dx,dy;
static int captured[3];
void __real_platformBlitSurface(PlatformSurface *,PlatformRect *,PlatformSurface *,PlatformRect *);
void __wrap_platformBlitSurface(PlatformSurface *s,PlatformRect *sr,PlatformSurface *d,PlatformRect *dr) {
    __real_platformBlitSurface(s,sr,d,dr);
}
static void observe(struct TTtmSlot *slot,int x,int y,uint16 frame,uint16 image,int flip) {
    if(!enabled || image>=MAX_BMP_SLOTS || !slot->bmpNames[image] ||
       strcmp(slot->bmpNames[image],"MJFISH3.BMP") || frame<8 || frame>10) return;
    PlatformSurface *s=slot->sprites[image][frame];
    pending=1;frame_no=frame;flip_no=flip;px=x;py=y;dx=grDx;dy=grDy;
    pw=platformGetSurfaceWidth(s);ph=platformGetSurfaceHeight(s);
    printf("FISH DRAW: frame=%d flip=%d x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d ticks=%d\n",frame,flip,x,y,dx,dy,grScale,pw,ph,ticks);
}
void __real_grDrawSprite(PlatformSurface *,struct TTtmSlot *,int,int,uint16,uint16);
void __wrap_grDrawSprite(PlatformSurface *s,struct TTtmSlot *slot,int x,int y,uint16 f,uint16 i) {
    __real_grDrawSprite(s,slot,x,y,f,i);observe(slot,x,y,f,i,0);
}
void __real_grDrawSpriteFlip(PlatformSurface *,struct TTtmSlot *,int,int,uint16,uint16);
void __wrap_grDrawSpriteFlip(PlatformSurface *s,struct TTtmSlot *slot,int x,int y,uint16 f,uint16 i) {
    __real_grDrawSpriteFlip(s,slot,x,y,f,i);observe(slot,x,y,f,i,1);
}
void __real_eventsWaitTick(uint16);
void __wrap_eventsWaitTick(uint16 n) { __real_eventsWaitTick(n); if(enabled) ticks+=n; }
void __real_platformUpdateWindow(PlatformWindow *);
void __wrap_platformUpdateWindow(PlatformWindow *window) {
    __real_platformUpdateWindow(window);
    if(!enabled) return;
    displays++;
    if(!pending) return;
    pending=0;
    if(captured[frame_no-8]) return;
    PlatformSurface *s=platformGetWindowSurface(window);
    int w=platformGetSurfaceWidth(s),h=platformGetSurfaceHeight(s),pitch=platformGetSurfacePitch(s);
    const unsigned char *pixels=platformGetSurfacePixels(s);
    if(w!=grRenderWidth || h!=grRenderHeight || w>1280 || platformGetSurfaceBytesPerPixel(s)!=4) exit(70);
    char path[64];snprintf(path,sizeof(path),"fish-%03d.ppm",frame_no);
    FILE *file=fopen(path,"wb");if(!file) exit(71);
    fprintf(file,"P6\n%d %d\n255\n",w,h);
    unsigned char row[1280*3];
    for(int y=0;y<h;y++) {
        const unsigned char *p=pixels+(size_t)y*pitch;
        for(int x=0;x<w;x++) {row[x*3]=p[x*4+2];row[x*3+1]=p[x*4+1];row[x*3+2]=p[x*4];}
        if(fwrite(row,3,w,file)!=(size_t)w) exit(72);
    }
    if(fclose(file)) exit(73);
    captured[frame_no-8]=1;
    printf("CAPTURE: frame=%d display=%d ticks=%d flip=%d x=%d y=%d dx=%d dy=%d canvas=%dx%d file=%s\n",frame_no,displays,ticks,flip_no,px,py,dx,dy,pw,ph,path);
    fflush(stdout);
}
int main(int argc,char **argv) {
    if(argc!=4 || !artStyleSelect(argv[3])) return 2;
    int tag=atoi(argv[1]),seed=atoi(argv[2]);
    debugMode=1;grWindowed=1;grForcedSeed=seed;evStartAtMaxSpeed=1;evHotKeysEnabled=1;soundDisabled=1;
    zipvfs_init("scrantic_data.zip");parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();soundInit();adsInit();
    printf("PALETTE: resource=%s index=0\n",palResources[0]->resName);
    for(int i=0;i<16;i++) printf("RGB: %d %d %d %d\n",i,palResources[0]->colors[i].r<<2,palResources[0]->colors[i].g<<2,palResources[0]->colors[i].b<<2);
    islandState.holiday=0;islandState.night=0;islandState.lowTide=0;islandState.raft=0;islandState.xPos=0;islandState.yPos=0;
    adsInitIsland();
    struct TTtmSlot slot;struct TTtmThread threads[MAX_TTM_THREADS]={0};
    const char *script=tag==29 ? "MJFISH.TTM" : "MJFISHC.TTM";
    int setup=tag==29 ? 1 : 43;
    ttmInitSlot(&slot);ttmLoadTtm(&slot,script);
    struct TTtmThread *t=&threads[0];t->ttmSlot=&slot;t->isRunning=TTM_RUNNING;
    t->sceneTag=setup;t->ip=ttmFindTag(&slot,setup);t->delay=4;t->fgColor=t->bgColor=15;t->ttmLayer=grNewLayer();
    printf("SETUP: direct original %s tag%d resource-load setup on adsInitIsland context\n",script,setup);
    while(t->isRunning==TTM_RUNNING) ttmPlay(t);
    printf("SCENE: TTM=%s tag=%d seed=%d day=1 low=0 raft=0 offset=0,0 render=%dx%d mode=direct-source-tag\n",script,tag,seed,grRenderWidth,grRenderHeight);
    t->sceneTag=tag;t->ip=ttmFindTag(&slot,tag);t->isRunning=TTM_RUNNING;grUpdateDelay=0;
    enabled=1;
    while(t->isRunning==TTM_RUNNING) {
        ttmPlay(t);grUpdateDisplay(threads,NULL,NULL);grUpdateDelay=t->delay;
    }
    enabled=0;
    printf("RETURN: displays=%d ticks=%d captured=%d,%d,%d\n",displays,ticks,captured[0],captured[1],captured[2]);
    grFreeLayer(t->ttmLayer);ttmResetSlot(&slot);
    adsReleaseIsland();soundEnd();graphicsEnd();zipvfs_shutdown();puts("DONE: direct native TTM returned and cleanup complete");
    return 0;
}
