#include<bits/stdc++.h>
using namespace std;
#define int long long
#include "structs.cpp"
double eps = 1e-5;

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
    if (argc <= 4){
        cout << "Please send 4 arguments: costTime Data_may Data_donhang outputFileName" << endl;
        return 0;
    }

    ifstream costInput(argv[1]);
    for (int i = 0; i < weekLength; ++i){
        costInput >> EcostAt[i];
    }
    for (int i = 0; i < weekLength; ++i){
        costInput >> WcostAt[i];
    }

    ifstream machineInput(argv[2]);
    vector<TMachine> machines;
    machineInput >> machines;

    ifstream orderInput(argv[3]);
    vector<TOrder> orders;
    orderInput >> orders;

    freopen(argv[4], "w", stdout);
    TOrderSolver orderSolver(machines);
    for (auto &order : orders){
        orderSolver.setOrder(order);
        orderSolver.bestSolutionCost();
    }

    int cnt = 0;
    for (auto machine : orderSolver.machines){
        for (auto &busyTime : machine.busyTimes)
            cnt += (int)busyTime.size() - 1;
    }
    cout << cnt << endl;
    for (auto machine : orderSolver.machines){
        int id = 0;
        for (auto &busyTime : machine.busyTimes){
            for (const auto &x : busyTime){
                if (x != *busyTime.begin())
                cout << machine.name << "_" << id << ' ' << machine.timeMapName[x] << ' '
                << x.first*blockLengthBySec << ' ' << x.second*blockLengthBySec << endl;
            }
            ++id;
        }
    }
}
