#include <graphics.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    circle(320, 240, 50);
    outtextxy(250, 240, (char*)"Hello Graphics!");
    
    getch();
    closegraph();
    return 0;
}
