from det3d.core.bbox.box_np_ops import center_to_corner_box3d
import open3d as o3d
import numpy as np 
import pickle
import os
import time

def corners_to_lines(qs, color=[204/255, 0, 0]):
    """ Draw 3d bounding box in image
        qs: (8,3) array of vertices for the 3d box in following order:
        7 -------- 4
       /|         /|
      6 -------- 5 .
      | |        | |
      . 3 -------- 0
      |/         |/
      2 -------- 1
    """
    idx = [(1,0), (5,4), (2,3), (6,7), (1,2), (5,6), (0,3), (4,7), (1,5), (0,4), (2,6), (3,7)]
    cl = [color for i in range(12)]
    
    # create a line set with vertices and indices
    lines = o3d.geometry.LineSet()
    lines.points = o3d.utility.Vector3dVector(qs)
    lines.lines = o3d.utility.Vector2iVector(idx)

    # set colors of the lines
    lines.colors = o3d.utility.Vector3dVector(cl)

    return lines

def plot_boxes(boxes, score_thresh):
    visuals =[] 
    num_det = boxes.shape[0]
    print('result row is: ', num_det)
    for i in range(num_det):
        score = boxes[i][9]
        if score < score_thresh:
            continue 

        box = boxes[i:i+1]
        print('box.shape')
        print(box.shape)
        corner = center_to_corner_box3d(box[:, :3], box[:, 3:6], box[:, 8])[0].tolist()
        visuals.append(corners_to_lines(corner, [1, 0, 0]))
    return visuals

def load_data(file_idx, bin_files):
    data_file = bin_files[file_idx]
    txt_file = data_file + '.txt'
    
    data_orig = np.fromfile(os.path.join('./lidars', data_file), dtype=np.float32)
    data_reshape = data_orig.reshape(-1,5)
    xyz = data_reshape[:, :3]
    boxes = np.loadtxt(os.path.join('./results', txt_file), dtype=np.float32)

    return xyz, boxes

def update_visualizer(vis, pcd, visual_boxes, file_idx, bin_files):
    xyz, boxes = load_data(file_idx, bin_files)
    
    # 移除之前的几何体
    vis.remove_geometry(pcd)
    for visual_box in visual_boxes:
        vis.remove_geometry(visual_box)

    # 更新点云数据
    pcd.points = o3d.utility.Vector3dVector(xyz)
    vis.add_geometry(pcd)

    # 更新框
    visual_boxes.clear()
    new_boxes = plot_boxes(boxes, 0.5)
    for visual_box in new_boxes:
        vis.add_geometry(visual_box)
        visual_boxes.append(visual_box)

def main():
    # 列出并排序bin文件
    bin_files = sorted([f for f in os.listdir('./lidars') if f.endswith('.bin')])
    
    # 初始化文件索引
    file_idx = [0]

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="pointcloud_display")
    vis.get_render_option().point_size = 1
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0, 0, 0])

    # 创建点云和框的列表
    pcd = o3d.geometry.PointCloud()
    visual_boxes = []

    # 加载并显示第一帧数据
    update_visualizer(vis, pcd, visual_boxes, file_idx[0], bin_files)

    while True:
        vis.poll_events()
        vis.update_renderer()

        # 每隔2秒自动更新到下一帧
        time.sleep(0.5)
        file_idx[0] += 1
        if file_idx[0] < len(bin_files):
            update_visualizer(vis, pcd, visual_boxes, file_idx[0], bin_files)
        else:
            vis.destroy_window()  # 如果没有更多的文件，关闭可视化器
            break

if __name__=="__main__":
    main()