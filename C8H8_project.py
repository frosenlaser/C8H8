import vtk

colors = vtk.vtkNamedColors()

def sphere_object(x, y, z, radius, my_color):    
    # создание сфер-атомов
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(x, y, z)
    sphereSource.SetRadius(radius)
    sphereSource.SetPhiResolution(100)
    sphereSource.SetThetaResolution(100)
    # мэппинг
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d(my_color))
    return actor

def cylinder_object(startPoint, endPoint, radius, my_color):
    # создание цилиндров-связей
    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetRadius(radius)
    cylinderSource.SetResolution(50)

    rng = vtk.vtkMinimalStandardRandomSequence()
    rng.SetSeed(8775070)
    normalizedX = [0] * 3
    normalizedY = [0] * 3
    normalizedZ = [0] * 3

    vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
    length = vtk.vtkMath.Norm(normalizedX)
    vtk.vtkMath.Normalize(normalizedX)

    arbitrary = [0] * 3
    for i in range(0, 3):
        rng.Next()
        arbitrary[i] = rng.GetRangeValue(-10, 10)
    vtk.vtkMath.Cross(normalizedX, arbitrary, normalizedZ)
    vtk.vtkMath.Normalize(normalizedZ)

    vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()
    matrix.Identity()
    for i in range(0, 3):
        matrix.SetElement(i, 0, normalizedX[i])
        matrix.SetElement(i, 1, normalizedY[i])
        matrix.SetElement(i, 2, normalizedZ[i])
    transform = vtk.vtkTransform()
    transform.Translate(startPoint)
    transform.Concatenate(matrix)
    transform.RotateZ(-90.0)
    transform.Scale(1.0, length, 1.0)
    transform.Translate(0, .5, 0)
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform)
    transformPD.SetInputConnection(cylinderSource.GetOutputPort())
    # мэппинг цилиндров
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    mapper.SetInputConnection(cylinderSource.GetOutputPort())
    actor.SetUserMatrix(transform.GetMatrix())
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d(my_color))
    return actor

def main():
    xCoordinates = []
    yCoordinates = []
    zCoordinates = []

    # задание исходных данных, считываю координаты атомов из файла
    sourceFile = open("C8H8_xyz.mol")
    for line in sourceFile:
        parameters = line.split()
        if len(parameters) == 9:
            xCoordinates.append(float(parameters[0]))
            yCoordinates.append(float(parameters[1]))
            zCoordinates.append(float(parameters[2]))
    sourceFile.close()
   
    # фильтрацию не провожу
    
    actor = []
    rad = 0.4
    
    # создаю сферы-атомы углерода
    for i in range(0, 8):
        actor.append(sphere_object(xCoordinates[i], yCoordinates[i], zCoordinates[i], rad, "ivory_black"))
    # создаю сферы-атомы водорода
    for i in range(8, 16):
        actor.append(sphere_object(xCoordinates[i], yCoordinates[i], zCoordinates[i], rad, "Snow"))
    
    # добавляю цилиндры-связи атомов
    binding1 = []
    binding2 = []
    sourceFile1 = open("C8H8_binding.mol")
    for line in sourceFile1:
        parameters = line.split()
        if len(parameters) == 6:
            binding1.append(int(parameters[0]) - 1)
            binding2.append(int(parameters[1]) - 1)
    sourceFile1.close()
    
    startPoints = []
    endPoints = []
    for i in range(len(binding1)):
        startPoint1 = [xCoordinates[binding1[i]], yCoordinates[binding1[i]], zCoordinates[binding1[i]]]
        endPoint1 = [xCoordinates[binding2[i]], yCoordinates[binding2[i]], zCoordinates[binding2[i]]]
        startPoints.append(startPoint1)
        endPoints.append(endPoint1)
        
    for i in range(len(binding1)):
        actor.append(cylinder_object(startPoints[i], endPoints[i], rad / 2.5, "rose_madder"))

    # рендеринг
    #camera = vtk.vtkCamera()
    #camera.SetPosition(0, 0, 15)
    #camera.SetFocalPoint(0, 0, 0)
    
    renderer = vtk.vtkRenderer()
   # renderer.SetActiveCamera(camera)
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(500, 500)
    renderWindow.SetWindowName("C8H8")
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    for i in range(len(xCoordinates)+len(binding1)):
        renderer.AddActor(actor[i])
    
    renderer.SetBackground(colors.GetColor3d("SkyBlue"))

    renderWindow.Render()
    renderWindowInteractor.Start()

if __name__ == '__main__':
    main()
