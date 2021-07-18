#include<bits/stdc++.h>
using namespace std;
#define int long long
#include "structs.cpp"
double eps = 1e-5;

#define debug(a) cerr<<#a<<" = "<<a<<endl;

struct TOrderSolver{
    TOrder order;
    vector<int> orderMachineIds;
    vector<TMachine> machines;
    vector<vector<double>> f;

    TOrderSolver(const vector<TMachine>& machines){
        this->machines = machines;
    }

    void setOrder(const TOrder& order){
        this->order = order;
        orderMachineIds.clear();
        for (auto &name : order.machineNames){
            for (auto &machine : machines){
                if (machine.name == name){
                    orderMachineIds.push_back(&machine - &machines[0]);
                    break;
                }
            }
        }
        assert(orderMachineIds.size() == order.machineNames.size());
        tmpString = order.name;
    }

    double bestSolutionCost(){
        if (order.deadLine < startTime){
            //cerr << "Don hang " << order.name <<" da qua han" << endl;
            return 1e18;
        }
    	f.assign(orderMachineIds.size(), vector<double>(order.deadLine - startTime, -1));
        int i = 0, t = startTime;
        while (i < order.machineNames.size()){
        	assert(t < order.deadLine);
        	if (t >= order.deadLine) break;
        	if (abs(dp(i, t) - dp(i, t+1)) <= eps){//skip this moment
        		++t;
        		continue;
        	}
        	int id = orderMachineIds[i];
	        int dt = (order.numOfCards + machines[id].cardPerBlock - 1) / machines[id].cardPerBlock;
	        machines[id].setWork(t, t+dt-1);
	        i += 1;
	        t += dt;
        }
        return dp(0, startTime);
    }

    double dp(int i, int t){//index of machine, time
        if (t >= order.deadLine) return 1e18;
        if (i == orderMachineIds.size()) return 0;
        auto &ans = f[i][t-startTime];
        if (ans >= eps) return ans;
        ans = 1e18;
        ans = dp(i, t+1);
        int id = orderMachineIds[i];
        int dt = (order.numOfCards + machines[id].cardPerBlock - 1) / machines[id].cardPerBlock;
        double tmp = machines[id].costToSolve(order.numOfCards, t);
        ans = min(ans, tmp + dp(i+1, t+dt));
        return ans;
    }

};

int deadLine(TOrderSolver orderSolver, TOrder order){
    orderSolver.setOrder(order);
    int L = startTime, H = L+1e6, ans = -1;

}

int32_t main(int32_t argc,char** argv){
    if (argc <= 2){
        cout << "Please send at least 2 arguments: inputFileName(xyzt) outputFileName [costTime] [Data_may]" << endl;
        return 0;
    }

    ifstream costInput(argc > 3 ? argv[3] : "costTime.txt");
    for (int i = 0; i < weekLength; ++i){
        costInput >> EcostAt[i];
    }
    for (int i = 0; i < weekLength; ++i){
        costInput >> WcostAt[i];
    }

    ifstream machineInput(argc > 4 ? argv[4] : "Data_may.txt");
    vector<TMachine> machines;
    machineInput >> machines;

    freopen(argv[1], "r", stdin);
    freopen(argv[2], "w", stdout);
    int cnt;
    cin >> cnt;
    while (cnt--){
        string machineName, orderName;
        int L, H;
        if (!(cin >> machineName >> orderName >> L >> H)){
            cerr << "Read input error" << endl;
            return 0;
        }
        L /= blockLengthBySec, H /= blockLengthBySec;

        int id = 0, power = 1;
        while (machineName.back() != '_'){
            //assert
            id += (machineName.back() - '0') * power;
            power *= 10;
            machineName.pop_back();
        }
        //assert
        machineName.pop_back();

        int i = 0;
        while (i < machines.size() && machines[i].name != machineName) ++i;
        assert(i < machines.size());
        assert(id < machines[i].busyTimes.size());
        assert(machines[i].isFree(id, L, H));
        machines[i].setWork(L, H, id);
    }

    double ans = 0;
    for (auto machine : machines){
        ans += machine.currentCost();
    }
    cout << ans << endl;
}
