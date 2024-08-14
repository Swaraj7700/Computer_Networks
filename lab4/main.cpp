#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <thread>    // For std::this_thread::sleep_for
#include <chrono>    // For std::chrono::seconds

#define TOTAL_PACKETS 10
#define WINDOW_SIZE 4
#define LOSS_RATE 20  // Percentage of packet loss

enum Protocol {
    GO_BACK_N,
    SELECTIVE_REPEAT
};

class SlidingWindow {
private:
    int base;
    int nextSeqNum;
    int protocol;
    std::vector<int> window;
    std::vector<bool> ackReceived;

public:
    SlidingWindow(int protocolType) : base(0), nextSeqNum(0), protocol(protocolType) {
        window.resize(TOTAL_PACKETS, -1);
        ackReceived.resize(TOTAL_PACKETS, false);
    }

    void sendPackets() {
        while (base < TOTAL_PACKETS) {
            for (int i = 0; i < WINDOW_SIZE && nextSeqNum < TOTAL_PACKETS; i++) {
                if (window[base + i] == -1) {
                    sendPacket(nextSeqNum);
                    nextSeqNum++;
                }
            }

            receiveAcks();
            slideWindow();
            std::this_thread::sleep_for(std::chrono::seconds(1)); // Simulating delay
        }
    }

private:
    void sendPacket(int seqNum) {
        window[seqNum] = seqNum;
        std::cout << "Sent packet: " << seqNum << std::endl;
    }

    void receiveAcks() {
        for (int i = base; i < base + WINDOW_SIZE && i < TOTAL_PACKETS; i++) {
            if (ackReceived[i] == false) {
                if (simulatePacketLoss()) {
                    std::cout << "Packet " << i << " lost.\n";
                } else {
                    ackReceived[i] = true;
                    std::cout << "Received ACK for packet: " << i << std::endl;
                }
            }
        }
    }

    void slideWindow() {
        if (protocol == GO_BACK_N) {
            for (int i = base; i < base + WINDOW_SIZE && i < TOTAL_PACKETS; i++) {
                if (ackReceived[i] == false) {
                    nextSeqNum = i;
                    break;
                } else {
                    base++;
                }
            }
        } else if (protocol == SELECTIVE_REPEAT) {
            while (ackReceived[base] == true && base < TOTAL_PACKETS) {
                base++;
            }
        }
    }

    bool simulatePacketLoss() {
        return (rand() % 100) < LOSS_RATE;
    }
};

int main() {
    srand(time(0));

    std::cout << "Go-Back-N Protocol Simulation:\n";
    SlidingWindow gbn(GO_BACK_N);
    gbn.sendPackets();

    std::cout << "\nSelective Repeat Protocol Simulation:\n";
    SlidingWindow sr(SELECTIVE_REPEAT);
    sr.sendPackets();

    return 0;
}
