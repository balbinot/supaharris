#USED to project Aitoff data points and grid lines (assumes input in degrees)
import numpy as np
import matplotlib.pyplot as plt

degrad = np.pi/180.

def project(li,bi,lz):
   sa = li-lz
   if len(sa) == 1:
      sa = np.zeros(1)+sa

   x180 = np.where(sa >= 180.0)

   sa = sa
   sa[x180] = sa[x180]-360.0*abs(np.cos(lz*degrad/2.))#uncomment b=0


   alpha2 = sa*degrad/2.
   delta = bi*degrad

   r2 = np.sqrt(2.)
   f = 2.*r2/np.pi

   cdec = np.cos(delta)
   denom = np.sqrt(1.+cdec*np.cos(alpha2))

   xx = cdec*np.sin(alpha2)*2.*r2/denom
   yy = np.sin(delta)*r2/denom

   xx = xx*(1./degrad)/f
   yy = yy*(1./degrad)/f
   return xx,yy


def project_grid(li,bi):



   sa = -(li-180.) #UNCOMENT lz=0


   alpha2 = sa*degrad/2.
   delta = bi*degrad

   r2 = np.sqrt(2.)
   f = 2.*r2/np.pi

   cdec = np.cos(delta)
   denom = np.sqrt(1.+cdec*np.cos(alpha2))

   xx = cdec*np.sin(alpha2)*2.*r2/denom
   yy = np.sin(delta)*r2/denom

   xx = xx*(1./degrad)/f
   yy = yy*(1./degrad)/f
   return xx,yy

def air_plot(Lex,Bex,Lex1,Bex1,X,Y,XX,YY,lz):

   plt.plot(X,Y,color='black')
   plt.plot(XX.T,YY.T,color='black')


   #GRID LABELS

   for i in range(len(Lex)):
      if Lex[i] <= lz:
         fitter = XX[i]-8
      else:
         fitter = XX[i]+3
      if Lex[i] < 0:
         Lex[i]=Lex[i]+360
      if Lex[i] != 360.:

         plt.text(fitter,0,str(int(Lex[i])),fontsize=12,rotation=90)

   for i in range(len(Bex1)):
      if Bex1[i] > 0.:
         fitter = YY1[i]+1
      else:
         fitter = YY1[i]-6
      plt.text(1,fitter,str(int(Bex1[i])),fontsize=12)
   #END GRID LABELS

def gridlines(lz,fig,ax):
   Lex = np.linspace(0,360,9)
   Bex = np.linspace(0,180,180)-90.
   Lex1 = np.linspace(0,360,360)
   Bex1 = np.linspace(0,180,7)-90.
   Lgrid,Bgrid = np.meshgrid(Lex,Bex)
   Lgrid1,Bgrid1 = np.meshgrid(Lex1,Bex1)
   X,Y = project_grid(Lgrid,Bgrid)
   XX,YY = project_grid(Lgrid1,Bgrid1)
   ax.plot(X,Y,'--',color='black')
   ax.plot(XX.T,YY.T,'--',color='black')



   for i in range(len(Lex)):
      if Lex[i] <= lz:
         fitter = X[int(X.shape[0]/2),Lex.size-1-i]-8
      else:
         fitter = X[int(X.shape[0]/2),Lex.size-1-i]+3
      Lex[i] = Lex[i]-180.-lz
      if Lex[i] < 0:
         Lex[i]=Lex[i]+360.
      if Lex[i] != 360.:

         ax.text(fitter,0,str(int(Lex[i])),fontsize=12,rotation=90)

   for i in range(len(Bex1)):
      if Bex1[i] > 0.:
         fitter = YY[i,int(len(YY[i])/2)]+1
      else:
         fitter = YY[i,int(len(YY[i])/2)]-6
      ax.text(1,fitter,str(int(Bex1[i])),fontsize=12)
   fig.gca().get_xaxis().set_visible(False)
   fig.gca().get_yaxis().set_visible(False)
