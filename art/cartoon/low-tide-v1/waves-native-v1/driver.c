/* Narrow observer extension. The engine and retained observer remain unchanged. */
#define main ancestor_main
#define __wrap_platformBlitSurface ancestor_platformBlitSurface
#define __wrap_grDrawSprite ancestor_grDrawSprite
#include "../../shoreline-repair-v1/integrated-shore-v1/native/driver.c"
#undef main
#undef __wrap_platformBlitSurface
#undef __wrap_grDrawSprite

void __wrap_platformBlitSurface(PlatformSurface *src, PlatformRect *sr,
                               PlatformSurface *dst, PlatformRect *dr)
{
    if (active_wave>=30 && active_wave<=41 && dr)
        printf("LOW SURFACE: frame=%d x=%d y=%d canvas=%dx%d\n",active_wave,dr->x,dr->y,
               platformGetSurfaceWidth(src),platformGetSurfaceHeight(src));
    ancestor_platformBlitSurface(src,sr,dst,dr);
}

void __wrap_grDrawSprite(PlatformSurface *s,struct TTtmSlot *slot,
                        int x,int y,uint16 frame,uint16 image)
{
    ancestor_grDrawSprite(s,slot,x,y,frame,image);
    if (image<MAX_BMP_SLOTS && slot->bmpNames[image] && !strcmp(slot->bmpNames[image],"MRAFT.BMP")) {
        PlatformSurface *sprite=slot->sprites[image][frame];
        printf("RAFT DRAW: frame=%u x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d\n",
               frame,x,y,grDx,grDy,grScale,platformGetSurfaceWidth(sprite),platformGetSurfaceHeight(sprite));
    }
}

int main(int argc,char **argv)
{
    if(argc!=9) return 2;
    int raft=atoi(argv[8]);
    if(raft<0 || raft>5) return 2;
    islandState.raft=raft;
    return ancestor_main(argc-1,argv);
}
