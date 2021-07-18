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

main(){
    ifstream costInput("costTime.txt");
    for (int i = 0; i < weekLength; ++i){
        costInput >> EcostAt[i];
    }
    for (int i = 0; i < weekLength; ++i){
        costInput >> WcostAt[i];
    }

    ifstream machineInput("Data_may.txt");
    vector<TMachine> machines;
    machineInput >> machines;

    ifstream orderInput("Data_donhang.txt");
    vector<TOrder> orders;
    orderInput >> orders;

    TOrderSolver orderSolver(machines);
    for (auto &order : orders){
        orderSolver.setOrder(order);
        cout << "Cost of " << order.name << ": " << orderSolver.bestSolutionCost() << endl;
        for (auto machine : orderSolver.machines){
            machine.output();
        }
    }
}
