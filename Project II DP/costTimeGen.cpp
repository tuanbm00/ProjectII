#include <bits/stdc++.h>
using namespace std;

#define all(s) s.begin(), s.end()
#define pb push_back
#define ii pair<int, int>
#define x first
#define y second
#define bit(x, y) ((x >> y) & 1)

int main() {
    ios::sync_with_stdio(false); cin.tie(0); 
    cout.tie(0);
    ofstream writer;
    writer.open("costTime.txt");

    for (int i = 0; i < 7; i++) {
        for (int j = 0; j < 24; j++) {
            if ((j >= 1 && j <= 5)) writer << 1 << ' ';
            else if (j >= 17 && j <= 21) writer << 3 << ' ';
            else writer << 2 << ' ';
        }
    }
    writer << endl;

    for (int i = 0; i < 7; i++) {
        for (int j = 0; j < 24; j++) {
            if (i == 6) {
                writer << 100000 << ' ';
                continue;
            }
            if ((j >= 8 && j <= 12) || (j >= 14 && j <= 18)) writer << 20 << ' ';
            else if (j >= 19 && j <= 23) writer << 30 << ' ';
            else writer << 100000 << ' ';
        }
    }

    return 0;
}