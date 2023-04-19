from det3d.core.bbox.box_np_ops import center_to_corner_box3d
import open3d as o3d
import numpy as np 
import pickle 

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

def main():
    # obj = pickle.load(open('/home/xiaxinkai/github/WaymoSeq1/lidar/seq_1_frame_1.pkl', 'rb'))
    # lidars = obj['lidars']
    # xyz = lidars['points_xyz']

    data_orig = np.fromfile('./lidars/seq_0_frame_100.bin', dtype=np.float32)
    data_reshape = data_orig.reshape(-1,5)
    xyz=data_reshape[:, :3]

    print(data_orig.shape)
    print(data_reshape.shape)
    print(xyz.shape)

    boxes = np.loadtxt('./results/seq_0_frame_100.bin.txt', dtype=np.float32)
    print(boxes.shape)

    #创建窗口对象
    vis = o3d.visualization.Visualizer()
    # #设置窗口标题
    vis.create_window(window_name="pointcloud_display")
    #设置点云大小
    vis.get_render_option().point_size = 1
    #设置颜色背景为黑色
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0, 0, 0])

    #创建点云对象
    pcd=o3d.open3d.geometry.PointCloud()
    #将点云数据转换为Open3d可以直接使用的数据类型
    pcd.points = o3d.utility.Vector3dVector(xyz)
    #设置点的颜色为白色
    pcd.paint_uniform_color([1,1,1])
    #将点云加入到窗口中
    vis.add_geometry(pcd)

    visual_boxes = plot_boxes(boxes, 0.5)
    for item in visual_boxes:
        print(type(item))
    for visual_box in visual_boxes:
        vis.add_geometry(visual_box)

    vis.run()
    vis.destroy_window()


if __name__=="__main__":
    main()