
#include <stdio.h>
#include <stdlib.h>
#include "mytypes.h"
#include "graphics.h"
#include "walk.h"
#include "art_style.h"
static int xx, yy, ff, flip;
static struct TTtmSlot *actor;
const TArtStyle *artStyleCurrent(void) { static TArtStyle style={"hd","HD","",2,1}; return &style; }
int zipvfs_exists(const char *p) { (void)p; return 0; }
void grClearScreen(PlatformSurface *s) { (void)s; }
void grDrawSprite(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    (void)s; (void)b; if(t==actor){xx=x;yy=y;ff=f;flip=0;}
}
void grDrawSpriteFlip(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    grDrawSprite(s,t,x,y,f,b); if(t==actor)flip=1;
}
void grDrawSpriteAtop(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    (void)s;(void)t;(void)x;(void)y;(void)f;(void)b;
}
int main(int argc,char **argv){
    if(argc!=6)return 2;
    struct TTtmSlot slot={0},bg={0}; struct TTtmThread thread={0};
    thread.ttmSlot=&slot; actor=&slot; srand((unsigned)atoi(argv[5]));
    walkInit(atoi(argv[1]),atoi(argv[2]),atoi(argv[3]),atoi(argv[4]));
    for(int n=0;n<1024;n++){
        uint16 delay=walkAnimate(&thread,&bg);
        if(!delay)return 0;
        printf("%d %d %d %d %d\n",ff,flip,xx,yy,delay);
    }
    return 3;
}
