#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/visualization/pcl_visualizer.h>

#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <boost/filesystem.hpp>

#include "render.h"

namespace fs = boost::filesystem;

bool spacePressed = false;

void keyboardEventOccurred(const pcl::visualization::KeyboardEvent& event, void* viewer_void) {
    if (event.getKeySym() == "space" && event.keyDown()) {
        spacePressed = true;
    }
}

std::vector<BoxQ> parseDetections(const std::string& filename) {
    std::vector<BoxQ> detections;
    std::ifstream in(filename);

    float x, y, z, length, width, height, yaw, confidence, _unused1, _unused2, _unused3;
    while (in >> x >> y >> z >> length >> width >> height >> _unused1 >> _unused2 >> yaw >> confidence >> _unused3) {
        BoxQ box;

        box.bboxTransform = Eigen::Vector3f(x, y, z);
        Eigen::AngleAxisf rotation_vector(-yaw, Eigen::Vector3f::UnitZ());
        box.bboxQuaternion = Eigen::Quaternionf(rotation_vector);
        box.cube_length = length;
        box.cube_width = width;
        box.cube_height = height;
        box.confidence = confidence;

        detections.push_back(box);
    }
    in.close();
    return detections;
}

int main() {
    // 获取bin文件列表并排序
    std::vector<std::string> binFiles;
    fs::path lidarPath("../../lidars/");
    for (fs::directory_iterator it(lidarPath); it != fs::directory_iterator(); ++it) {
        if (fs::is_regular_file(it->path()) && it->path().extension() == ".bin") {
            binFiles.push_back(it->path().string());
        }
    }
    std::sort(binFiles.begin(), binFiles.end());

    pcl::visualization::PCLVisualizer::Ptr viewer(new pcl::visualization::PCLVisualizer("3D Viewer"));
    viewer->registerKeyboardCallback(keyboardEventOccurred, (void*)viewer.get());
    int fileIndex = 0;

    int box_id = 0;

    while (!viewer->wasStopped()) {
        viewer->removeAllPointClouds();
        viewer->removeAllShapes();

        // 读取bin文件
        std::ifstream binFile(binFiles[fileIndex], std::ios::binary);
        pcl::PointCloud<pcl::PointXYZI>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZI>);

        float data[5];
        while (binFile.read(reinterpret_cast<char*>(data), sizeof(data))) {
            pcl::PointXYZI point;
            point.x = data[0];
            point.y = data[1];
            point.z = data[2];
            point.intensity = data[4];
            cloud->push_back(point);
        }
        binFile.close();

        // renderPointCloud(viewer, cloud, "cloud");
        viewer->addPointCloud<pcl::PointXYZI>(cloud, "sample cloud");

        // 读取txt文件
        std::string txtFile = "../../results/" + fs::path(binFiles[fileIndex]).filename().string() + ".txt";
        std::vector<BoxQ> boxes = parseDetections(txtFile);

        for (auto box : boxes)
        {
            if (box.confidence > 0.5)
            {
                renderBox(viewer, box, box_id);
                box_id++;
            }
        }

        // 在左下角显示文件名
        std::string currentFilename = fs::path(binFiles[fileIndex]).filename().string();
        int fontSize = 20; // 设定字体大小，你可以按需调整
        viewer->addText(currentFilename, 10, 30, fontSize, 1.0, 1.0, 1.0, "filenameText");

        viewer->spinOnce();

        if (spacePressed) {
            fileIndex = (fileIndex + 1) % binFiles.size();
            spacePressed = false;  // Reset the flag
        }
    }

    return 0;
}