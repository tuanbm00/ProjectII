
string timestemToString(time_t epoch_time) {
    tm *date;
    date = gmtime(&epoch_time);
    char s[100];
    sprintf(s, "%04d/%02d/%02d %02d:%02d:%02d", 1900 + date->tm_year, date->tm_mon, date->tm_mday, date->tm_hour, date->tm_min, date->tm_sec);
    return string(s);
}

const int blockLengthBySec = 60 * 60;//by second
const int weekLength = 60 * 60 * 24 * 7 / blockLengthBySec;//number of block per week
int startTime = time(0) /  blockLengthBySec;//the started block

int EcostAt[weekLength];
int WcostAt[weekLength];
string tmpString;

struct TMachine {

    string name;
    vector<int> costAt;
	double cardPerBlock;
	double kwPerBlock;
	double workerPerBlock;
    vector<set< pair<int,int> >> busyTimes;
    map<pair<int,int>, string> timeMapName;

    TMachine(){
        costAt.resize(weekLength);
    }

    TMachine(int numOfTMachine) {
        costAt.resize(weekLength);
        busyTimes.resize(numOfTMachine, set<pair<int,int>>({make_pair(startTime-1, startTime-1)}));
    }

    bool isFree(int machine_th, int L, int H){
        auto &S = busyTimes[machine_th];
        auto bL = *--S.upper_bound({L, 2e9});
        if (bL.second >= L) return false;
        auto bH = *--S.upper_bound({H, 2e9});
        return bL == bH;
    }

    int freeMachine(int L, int H){
        for (int i = 0; i < busyTimes.size(); ++i){
            if (isFree(i, L, H)) return i;
        }
        return -1;
    }

    void setWork(int L, int H, int machine_th=-1){
        if (machine_th == -1) machine_th = freeMachine(L, H);
        assert(machine_th>=0 && machine_th<busyTimes.size());
        assert(isFree(machine_th, L, H));
        busyTimes[machine_th].insert({L, H});
        timeMapName[{L,H}] = tmpString;
    }

	double costToSolve(int numOfCards, int t){
	 	double dt = (double)numOfCards / cardPerBlock;
	    int i = freeMachine(t, t + ceil(dt));
	    if (i == -1){
            return 1e18;
	    }
	    double ans = 0;
	    for (int j = t; j < t+dt; ++j){
            if (j+1 > t+dt) ans += costAt[j % weekLength] * (t + dt - j);
            else ans += costAt[j % weekLength];
	    }
	    return ans;
	}

	double currentCost(){
	    double ans = 0;
	    for (auto &busyTime : busyTimes){
            for (auto &x : busyTime){
                for (int j = x.first; j <= x.second; ++j){
                    ans += costAt[j % weekLength];
                }
            }
	    }
	    return ans;
	}

    void output(){
        for (auto& busyTime : busyTimes) if (busyTime.size() > 1){
            cout << name << " " << (&busyTime - &busyTimes[0]) << ":" << endl;
            for (auto e : busyTime) if (e != *busyTime.begin()){
                cout << timestemToString(e.first * blockLengthBySec) << " ... " << timestemToString((e.second+1) * blockLengthBySec) << endl;
            }
            cout << endl;
        }
    }
};


//TMachine io
istream& operator>>(istream& in, TMachine& machine){
    string a;
    double b, c, d;
    int e;
    in >> a >> b >> c >> d >> e;
    TMachine m = TMachine(e);
    m.name = a, m.cardPerBlock = b, m.kwPerBlock = c, m.workerPerBlock = d;
    for (auto x : {&m.cardPerBlock, &m.kwPerBlock, &m.workerPerBlock}){
        *x = (*x) * blockLengthBySec / 60 / 60;
    }
    for (int t = 0; t < weekLength; ++t){
        m.costAt[t] += m.kwPerBlock * EcostAt[t];
        m.costAt[t] += m.workerPerBlock * WcostAt[t];
    }
    //state
    for (auto &busyTime : m.busyTimes){
        int k;
        in >> k;
        while (k--){
            int L, H;
            in >> L >> H;
            busyTime.insert(make_pair(L, H));
        }
    }
    machine = m;
    return in;
}

ostream& operator<<(ostream& out, TMachine& m){
    out << m.name << '\n';
    for (auto x : {&m.cardPerBlock, &m.kwPerBlock, &m.workerPerBlock}){
        out << (*x) * 60 * 60 / blockLengthBySec << '\n';
    }
    out << m.busyTimes.size() << '\n';
    for (auto &busyTime : m.busyTimes){
        out << (int)busyTime.size() - 1 << ' ';
        for (const auto &x : busyTime){
            if (x != *busyTime.begin())
            out << x.first << ' ' << x.second << ' ';
        }
        out << '\n';
    }
    return out;
}

struct TOrder{
    string name;
	int numOfCards;
	vector<string> machineNames;
	int deadLine;
};

istream& operator >> (istream& in, TOrder &order){
    in >> order.name;
    in >> order.numOfCards;
    int k;
    in >> k;
    order.machineNames.resize(k);
    for (auto &name : order.machineNames) in >> name;
    in >> order.deadLine;
    order.deadLine /= blockLengthBySec;
}

ostream& operator << (ostream &out, const TOrder &order){
    out << order.name << '\n';
    out << order.numOfCards << '\n';
    out << order.machineNames.size() << '\n';
    for (auto &name : order.machineNames) out << name << '\n';
    out << order.deadLine * blockLengthBySec << '\n';
}

template<typename T>
istream& operator >> (istream& in, vector<T> &a){
    int n;
    in >> n;
    a.resize(n);
    for (T &x : a) in >> x;
    return in;
}

template<typename T>
ostream& operator << (ostream& out, vector<T> &a){
    out << "( ";
    for (T &x : a) out << x << ' ';
    out << ')' << endl;
    return out;
}
