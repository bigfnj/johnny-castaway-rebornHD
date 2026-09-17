/* Diagnostic observer. Real engine calls and native background timers are retained. */
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

static int capture_enabled, display_number, clock_ticks, active_ground;
static int active_wave=-1;
static int phases[4] = {-1,-1,-1,-1};
static int johnny[4] = {-1,0,0,0};
static int segment_number;

void __real_platformBlitSurface(PlatformSurface *, PlatformRect *, PlatformSurface *, PlatformRect *);
void __wrap_platformBlitSurface(PlatformSurface *src, PlatformRect *sr, PlatformSurface *dst, PlatformRect *dr)
{
    if (active_ground && dr)
        printf("GROUND SURFACE: x=%d y=%d canvas=%dx%d\n", dr->x, dr->y,
               platformGetSurfaceWidth(src), platformGetSurfaceHeight(src));
    if (active_wave>=3 && active_wave<=11 && dr)
        printf("WAVE SURFACE: frame=%d x=%d y=%d canvas=%dx%d\n",active_wave,dr->x,dr->y,
               platformGetSurfaceWidth(src),platformGetSurfaceHeight(src));
    __real_platformBlitSurface(src,sr,dst,dr);
}

static void observe(struct TTtmSlot *slot,int x,int y,uint16 frame,uint16 image,int flip)
{
    if (image>=MAX_BMP_SLOTS || !slot->bmpNames[image]) return;
    const char *name=slot->bmpNames[image];
    PlatformSurface *s=slot->sprites[image][frame];
    if (!strcmp(name,"BACKGRND.BMP")) {
        printf("BG DRAW: frame=%u x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d\n",
               frame,x,y,grDx,grDy,grScale,platformGetSurfaceWidth(s),platformGetSurfaceHeight(s));
        if(frame>=3 && frame<=11) phases[(frame-3)/3]=frame;
        if(frame>=30 && frame<=41) phases[(frame-30)/3]=frame;
    }
    if (!strcmp(name,"HOLIDAY.BMP"))
        printf("PROP DRAW: frame=%u x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d\n",
               frame,x,y,grDx,grDy,grScale,platformGetSurfaceWidth(s),platformGetSurfaceHeight(s));
    if (!strcmp(name,"JOHNWALK.BMP")) {
        johnny[0]=frame; johnny[1]=flip; johnny[2]=x; johnny[3]=y;
        printf("JOHNNY DRAW: segment=%d frame=%u flip=%d x=%d y=%d\n",segment_number,frame,flip,x,y);
    }
}

void __real_grDrawSprite(PlatformSurface *,struct TTtmSlot *,int,int,uint16,uint16);
void __wrap_grDrawSprite(PlatformSurface *s,struct TTtmSlot *slot,int x,int y,uint16 frame,uint16 image)
{
    active_ground=image<MAX_BMP_SLOTS && slot->bmpNames[image] &&
                  !strcmp(slot->bmpNames[image],"BACKGRND.BMP") && frame==0;
    active_wave=image<MAX_BMP_SLOTS && slot->bmpNames[image] &&
                !strcmp(slot->bmpNames[image],"BACKGRND.BMP") ? frame : -1;
    __real_grDrawSprite(s,slot,x,y,frame,image);
    active_ground=0;
    active_wave=-1;
    observe(slot,x,y,frame,image,0);
}
void __real_grDrawSpriteFlip(PlatformSurface *,struct TTtmSlot *,int,int,uint16,uint16);
void __wrap_grDrawSpriteFlip(PlatformSurface *s,struct TTtmSlot *slot,int x,int y,uint16 frame,uint16 image)
{
    __real_grDrawSpriteFlip(s,slot,x,y,frame,image);
    observe(slot,x,y,frame,image,1);
}
void __real_eventsWaitTick(uint16);
void __wrap_eventsWaitTick(uint16 ticks)
{
    __real_eventsWaitTick(ticks);
    if(capture_enabled) clock_ticks+=ticks;
}
void __real_platformUpdateWindow(PlatformWindow *);
void __wrap_platformUpdateWindow(PlatformWindow *window)
{
    __real_platformUpdateWindow(window);
    if(!capture_enabled) return;
    PlatformSurface *s=platformGetWindowSurface(window);
    int w=platformGetSurfaceWidth(s),h=platformGetSurfaceHeight(s),pitch=platformGetSurfacePitch(s);
    const unsigned char *pixels=platformGetSurfacePixels(s);
    if(w!=1280 || h!=960 || platformGetSurfaceBytesPerPixel(s)!=4) exit(70);
    char path[64]; snprintf(path,sizeof(path),"display-%03d.ppm",++display_number);
    FILE *file=fopen(path,"wb"); if(!file) exit(71);
    if(fprintf(file,"P6\n%d %d\n255\n",w,h)<0) exit(72);
    unsigned char row[1280*3];
    for(int y=0;y<h;y++) {
        const unsigned char *p=pixels+(size_t)y*pitch;
        for(int x=0;x<w;x++) {row[x*3]=p[x*4+2];row[x*3+1]=p[x*4+1];row[x*3+2]=p[x*4];}
        if(fwrite(row,3,w,file)!=(size_t)w) exit(73);
    }
    if(fclose(file)) exit(74);
    printf("DISPLAY: n=%d ticks=%d segment=%d phases=%d,%d,%d,%d johnny=%d,%d,%d,%d\n",
           display_number,clock_ticks,segment_number,phases[0],phases[1],phases[2],phases[3],johnny[0],johnny[1],johnny[2],johnny[3]);
}

static void walk(int a,int b,int c,int d)
{
    ++segment_number;
    printf("NATIVE CALL: segment=%d args=%d,%d,%d,%d\n",segment_number,a,b,c,d);
    adsPlayWalk(a,b,c,d);
    printf("NATIVE RETURN: segment=%d ticks=%d\n",segment_number,clock_ticks);
}

int main(int argc,char **argv)
{
    if(argc!=8 || !artStyleSelect("hd")) return 2;
    int holiday=atoi(argv[1]),night=atoi(argv[2]),x=atoi(argv[3]),y=atoi(argv[4]);
    int low=atoi(argv[5]),mode=atoi(argv[6]),waits=atoi(argv[7]);
    if(holiday<0 || holiday>4 || night<0 || night>1 || low<0 || low>1 || mode<0 || mode>2 || waits<1 || waits>40) return 2;
    debugMode=1;grWindowed=1;grForcedSeed=11;grCapturePath="final.ppm";
    evStartAtMaxSpeed=1;evHotKeysEnabled=1;soundDisabled=1;
    zipvfs_init("scrantic_data.zip");parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();soundInit();adsInit();
    islandState.holiday=holiday;islandState.night=night;islandState.lowTide=low;
    islandState.xPos=x;islandState.yPos=y;
    adsInitIsland();
    printf("STATE: seed=11 holiday=%d night=%d offset=%d,%d low=%d raft=%d render=%dx%d\n",
           holiday,night,x,y,low,islandState.raft,grRenderWidth,grRenderHeight);
    capture_enabled=1;
    if(mode==0) for(int i=0;i<waits;i++) walk(0,0,0,0);
    if(mode==1) {srand(2);walk(3,7,3,7);srand(2);walk(3,7,5,3);}
    if(mode==2) {srand(2);walk(1,3,1,3);srand(2);walk(1,3,4,5);}
    capture_enabled=0;
    adsReleaseIsland();soundEnd();graphicsEnd();zipvfs_shutdown();
    puts("DONE: native calls returned; cleanup complete");
    return 0;
}
