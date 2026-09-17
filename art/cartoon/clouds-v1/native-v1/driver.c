/* Explicit cloud fixtures; rendering, movement and scheduling remain native. */
#define main retained_main
#define __wrap_grDrawSprite retained_grDrawSprite
#define __wrap_grDrawSpriteFlip retained_grDrawSpriteFlip
#define __wrap_platformBlitSurface retained_platformBlitSurface
#include "../../shoreline-repair-v1/integrated-shore-v1/native/driver.c"
#undef main
#undef __wrap_grDrawSprite
#undef __wrap_grDrawSpriteFlip
#undef __wrap_platformBlitSurface

static int watching_cloud, blits, blit_left, blit_top, blit_right, blit_bottom;

void __wrap_platformBlitSurface(PlatformSurface *src, PlatformRect *sr,
                               PlatformSurface *dst, PlatformRect *dr)
{
    if (watching_cloud && dr) {
        int w=sr ? sr->w : platformGetSurfaceWidth(src);
        int h=sr ? sr->h : platformGetSurfaceHeight(src);
        if (!blits || dr->x<blit_left) blit_left=dr->x;
        if (!blits || dr->y<blit_top) blit_top=dr->y;
        if (!blits || dr->x+w>blit_right) blit_right=dr->x+w;
        if (!blits || dr->y+h>blit_bottom) blit_bottom=dr->y+h;
        ++blits;
    }
    retained_platformBlitSurface(src,sr,dst,dr);
}

static void cloud_begin(struct TTtmSlot *slot,uint16 frame,uint16 image)
{
    watching_cloud=capture_enabled && image<MAX_BMP_SLOTS &&
        slot->bmpNames[image] && !strcmp(slot->bmpNames[image],"BACKGRND.BMP") &&
        frame>=15 && frame<=17;
    blits=0;
}

static void cloud_end(struct TTtmSlot *slot,int x,int y,uint16 frame,uint16 image,int flip)
{
    if (watching_cloud) {
        PlatformSurface *s=slot->sprites[image][frame];
        printf("CLOUD DRAW: frame=%u flip=%d x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d blits=%d bounds=%d,%d,%d,%d\n",
               frame,flip,x,y,grDx,grDy,grScale,platformGetSurfaceWidth(s),
               platformGetSurfaceHeight(s),blits,blit_left,blit_top,blit_right,blit_bottom);
    }
    watching_cloud=0;
}

void __wrap_grDrawSprite(PlatformSurface *s,struct TTtmSlot *slot,
                        int x,int y,uint16 frame,uint16 image)
{
    cloud_begin(slot,frame,image);
    retained_grDrawSprite(s,slot,x,y,frame,image);
    cloud_end(slot,x,y,frame,image,0);
}

void __wrap_grDrawSpriteFlip(PlatformSurface *s,struct TTtmSlot *slot,
                            int x,int y,uint16 frame,uint16 image)
{
    cloud_begin(slot,frame,image);
    retained_grDrawSpriteFlip(s,slot,x,y,frame,image);
    cloud_end(slot,x,y,frame,image,1);
}

int main(int argc,char **argv)
{
    if (argc!=10 || !artStyleSelect("cartoon")) return 2;
    int holiday=atoi(argv[1]),night=atoi(argv[2]),x=atoi(argv[3]),y=atoi(argv[4]);
    int low=atoi(argv[5]),mode=atoi(argv[6]),waits=atoi(argv[7]);
    int wind=atoi(argv[8]),count=atoi(argv[9]);
    if (holiday!=0 || night<0 || night>1 || low!=0 || mode!=0 ||
        waits<1 || waits>40 || wind<0 || wind>1 || (count!=0 && count!=3)) return 2;
    debugMode=1;grWindowed=1;grForcedSeed=11;grCapturePath="final.ppm";
    evStartAtMaxSpeed=1;evHotKeysEnabled=1;soundDisabled=1;
    zipvfs_init("scrantic_data.zip");parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();soundInit();adsInit();
    islandState.holiday=holiday;islandState.night=night;islandState.lowTide=low;
    islandState.xPos=x;islandState.yPos=y;
    adsInitIsland();
    /* Replace only randomized cloud state after initialization. The first
       native timer-zero update clears the old layer before any capture. */
    const int xs[3]={40,230,375},ys[3]={25,55,30},speeds[3]={1,2,1};
    islandState.clouds.numClouds=count;islandState.clouds.windDirection=wind;
    for (int i=0;i<count;i++) {
        islandState.clouds.cloudNo[i]=i;
        islandState.clouds.xPos[i]=xs[i];islandState.clouds.yPos[i]=ys[i];
        islandState.clouds.windSpeed[i]=speeds[i];
    }
    printf("STATE: seed=11 holiday=%d night=%d offset=%d,%d low=%d raft=%d render=%dx%d\n",
           holiday,night,x,y,low,islandState.raft,grRenderWidth,grRenderHeight);
    printf("CLOUD FIXTURE: wind=%d count=%d source=explicit-native-state\n",wind,count);
    for (int i=0;i<count;i++)
        printf("CLOUD INITIAL: frame=%d x=%d y=%d speed=%d\n",15+i,xs[i],ys[i],speeds[i]);
    capture_enabled=1;
    for (int i=0;i<waits;i++) walk(0,0,0,0);
    capture_enabled=0;
    adsReleaseIsland();soundEnd();graphicsEnd();zipvfs_shutdown();
    puts("DONE: native calls returned; cleanup complete");
    return 0;
}
