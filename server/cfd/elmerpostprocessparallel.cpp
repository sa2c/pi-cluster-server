/*=========================================================================

Creates VTK files in the legacy format for the Elmer's output data.
One .vtk is created for each time step

Author: Dr. Chennakesava Kadapa
Date  : 27-Sept-2018
Place : Swansea, UK
=========================================================================*/


#include <vector>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <stdio.h>
#include <float.h>
#include <assert.h>
#include <fstream>
#include <iomanip>
#include <algorithm>
#include <iostream>


using namespace std;

struct fielddata
{
  vector<float> veloX, veloY, pres;

  void setsizes(int nNode)
  {
    veloX.resize(nNode, 0.0);
    veloY.resize(nNode, 0.0);
    pres.resize(nNode, 0.0);
  }
};


template<typename T>
void findUnique(vector<T>& vect)
{
  sort(vect.begin(), vect.end());
  vect.erase(unique(vect.begin(), vect.end()), vect.end());
}


/*
 * copied from stack exchange 
 * https://stackoverflow.com/questions/35301432/remove-extra-white-spaces-in-c
 */
void remove_extra_whitespaces(const string &input, string &output)
{
    output.clear();  // unless you want to add at the end of existing sring...
    unique_copy (input.begin(), input.end(), back_insert_iterator<string>(output),
                                     [](char a,char b){ return isspace(a) && isspace(b);});  
}

void split(const std::string &input, char delim, vector<string>& result)
{
    result.clear();
    std::stringstream ss(input);
    std::string item;
    while (std::getline(ss, item, delim))
    {
      result.push_back(item);
    }
}

/*
 * copied from 
 * https://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
 */
// trim from left
inline std::string& ltrim(std::string& s, const char* t = " \t\n\r\f\v")
{
    s.erase(0, s.find_first_not_of(t));
    return s;
}

/*
 * copied from 
 * https://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
 */
// trim from right
inline std::string& rtrim(std::string& s, const char* t = " \t\n\r\f\v")
{
    s.erase(s.find_last_not_of(t) + 1);
    return s;
}

/*
 * copied from 
 * https://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
 */
// trim from left & right
inline std::string& trim(std::string& s, const char* t = " \t\n\r\f\v")
{
    return ltrim(rtrim(s, t), t);
}


void  read_nodes(string& fname, int nNode, vector<int>& nodenums_local, vector<float>& xco, vector<float>& yco)
{
    ifstream fin(fname);

    if(fin.fail())
    {
      cout << " Could not open the Intput file" << '\t' << fname << endl;
      exit(1);
    }

    vector<string>  stringlist;

    // allocate space for storing the data
    if(xco.size() != nNode)
      xco.resize(nNode);
    if(yco.size() != nNode)
      yco.resize(nNode);


    string line;
    int nnum=0;
    while(getline(fin,line))
    {
      split(line, ' ', stringlist);

      nnum = stoi(stringlist[0])-1;

      nodenums_local.push_back(nnum);

      xco[nnum] = stof(stringlist[2]);
      yco[nnum] = stof(stringlist[3]);
      //zco[count] = stof(stringlist[4]);
    }

    fin.close();

    return;
}



void  read_elements(string& fname, vector<vector<int> >& elemNodeConn, vector<int>& elem_proc_id, int nproc)
{
    ifstream fin(fname);

    if(fin.fail())
    {
       cout << " Could not open the Intput file" << '\t' << fname << endl;
       exit(1);
    }

    vector<string>  stringlist;
    vector<int> vecTempInt(5);

    string line;
    int count=0, elnum;
    while(getline(fin,line))
    {
      split(line, ' ', stringlist);

      if(count > elemNodeConn.size())
      {
        elemNodeConn.reserve(elemNodeConn.size()*2);
        elem_proc_id.reserve(elemNodeConn.size()*2);
      }

      // element number
      elnum = stoi(stringlist[0])-1;

      elem_proc_id.push_back(nproc);

      vecTempInt[0] = elnum;
      vecTempInt[1] = stoi(stringlist[3])-1;
      vecTempInt[2] = stoi(stringlist[4])-1;
      vecTempInt[3] = stoi(stringlist[5])-1;

      //elemNodeConn[count] = vecTempInt;
      elemNodeConn.push_back(vecTempInt);

      //count++;
    }

    fin.close();

    return;
}


/*
 * Write the output in legacy VTK format
 * Author: Dr. Chennakesava Kadapa
 * Date  : 27-Sept-2018
 * Place : Swansea, UK
 */
void  writeoutputvtk(int nNode, int nElem, 
                    vector<float>& xco,
                    vector<float>& yco, 
                    vector<vector<int> >& elemNodeConn, 
                    vector<float>& veloX,
                    vector<float>& veloY,
                    vector<float>& pres,
                    vector<int>& elem_proc_id,
                    char* fname_vtk)
{
    ofstream fout(fname_vtk);

    if(fout.fail())
    {
      cout << " Could not open the output file" << '\t' << fname_vtk << endl;
      exit(1);
    }

    int ee, ii, jj;

    // Directives
    fout << "# vtk DataFile Version 4.0" << endl;
    fout << "Elmer simulation" << endl;

    // ASCII or Binary
    fout << "ASCII" << endl;

    // Type of dataset : Structured/Unstructured/Rectilinear/Polydata...
    fout << "DATASET UNSTRUCTURED_GRID" << endl;
      
    // Coordinates of the points (nodes)
    fout << "POINTS " << '\t' << nNode << " float" << endl;
    for(ii=0; ii<nNode; ++ii)
    {
      fout << xco[ii] << setw(10) << " " << yco[ii] << setw(10) << " " << 0.0 << endl;
    }

    // Element<->Nodes connectivity
    // In VTK terminology, Cell<->Points
    // <number of nodes> <n1> <n2> <n3> ...
    // Starting index is 0
    int npElem = 3;
    int ind = nElem*(npElem+1);
    fout << "CELLS " << '\t' << nElem << '\t' << ind << endl;

    // Linear Triangular element
    int n1 = 5;
    for(ee=0; ee<nElem; ++ee)
    {
      fout << npElem << setw(10) << " " << elemNodeConn[ee][0]  << setw(10) << " " << elemNodeConn[ee][1]  << setw(10) << " " << elemNodeConn[ee][2] << endl;
    }

    // Cell type, as per VTK
    fout << "CELL_TYPES" << '\t' << nElem << endl;
    for(ee=0; ee<nElem; ++ee)
    {
      fout << n1 << endl;
    }

    // Cell data
    fout << "CELL_DATA" << '\t' << nElem << endl;

    // pressure
    fout << "SCALARS procid int 1" << endl;
    fout << "LOOKUP_TABLE default" << endl;
    for(ii=0; ii<nElem; ++ii)
    {
      fout << elem_proc_id[ii] << endl;
    }

    // Point data
    fout << "POINT_DATA" << '\t' << nNode << endl;

    // pressure
    fout << "SCALARS pressure float 1" << endl;
    fout << "LOOKUP_TABLE default" << endl;
    for(ii=0; ii<nNode; ++ii)
    {
      fout << pres[ii] << endl;
    }

    fout << "VECTORS velocity float" << endl;
    for(ii=0; ii<nNode; ++ii)
    {
      fout << veloX[ii] << setw(16) << " " << veloY[ii] << setw(16) << " " << 0.0 << endl;
    }

    // close the file
    fout.close();

    return;
}


int main(int argc, char* argv[])
{
    if(argc < 3)
    {
      cerr << " Error in Input data " << endl;
      return 1;
    }


    vector<vector<int> >  elemNodeConn, elemNodeConn2;
    vector<int>  elem_proc_id2, vecTempInt3(3);
    vector<int>  elem_proc_id;

    cout << "Mesh file prefix         = " << argv[1] << endl;
    cout << "Field data file prefix   = " << argv[2] << endl;
    cout << "Number of processors     = " << argv[3] << endl;
    int nproc = atoi(argv[3]);


    cout << "\n\nReading elements" << endl;
    cout << "==========================\n\n" << endl;

    ////////////////////////////////////////////
    // read element-node connectivity
    int np=0, ee, ii, jj, kk, n1, n2, elnum;
    string fname_mesh(argv[1]);
    string fname_elems;
    char fname_temp[200];

    // allocate space for storing the data
    elemNodeConn2.reserve(10000);
    elem_proc_id.reserve(10000);

    for(np=0; np<nproc; ++np)
    {
      sprintf(fname_temp, "%s%s%d%s", fname_mesh.c_str(), ".",(np+1),".elements");
      fname_elems = fname_temp;
      cout << "Element file name # = " << fname_elems << endl;
      read_elements(fname_elems, elemNodeConn2, elem_proc_id2, (np+1));
    }
    int nElem = elemNodeConn2.size();
    cout << "Number of elements = " << nElem << endl;

    elemNodeConn.resize(nElem);
    vector<int>  nodes_unique;
    for(ee=0; ee<nElem; ee++)
    {
      elnum = elemNodeConn2[ee][0];

      vecTempInt3[0] = elemNodeConn2[ee][1];
      vecTempInt3[1] = elemNodeConn2[ee][2];
      vecTempInt3[2] = elemNodeConn2[ee][3];

      elemNodeConn[elnum] = vecTempInt3;
      elem_proc_id[elnum] = elem_proc_id2[ee];

      nodes_unique.push_back(vecTempInt3[0]);
      nodes_unique.push_back(vecTempInt3[1]);
      nodes_unique.push_back(vecTempInt3[2]);
    }

    findUnique(nodes_unique);
    int nNode = nodes_unique.size();
    cout << "Number of nodes = " << nNode << endl;

    ////////////////////////////////////////////
    // read nodal coordinates

    // find unique node numbers and
    // number of nodes

    cout << "\n\nReading nodal coordinates" << endl;
    cout << "==========================\n\n" << endl;

    vector<float>  xcoords(nNode, 0.0), ycoords(nNode, 0.0);
    vector<vector<int> >  nodenums_local;

    nodenums_local.resize(nproc);

    std::string fname_nodes;
    for(np=0; np<nproc; ++np)
    {
      sprintf(fname_temp, "%s%s%d%s", fname_mesh.c_str(), ".",(np+1),".nodes");
      fname_nodes = fname_temp;
      cout << "Element file name # = " << fname_nodes << endl;
      read_nodes(fname_nodes, nNode, nodenums_local[np], xcoords, ycoords);
    }

    ////////////////////////////////////////////
    // read the field data

    cout << "\n\nReading field data" << endl;
    cout << "==========================\n\n" << endl;

    string line, line2;
    vector<float>  veloX(nNode, 0.0), veloY(nNode, 0.0), pres(nNode, 0.0);
    int timesteps_default=100, timesteps_actual;

    vector<fielddata>  solution(timesteps_default);
    for(ii=0; ii<100; ++ii)
      solution[ii].setsizes(nNode);

    vector<float>  vecTempDbl(3);
    vector<int>   perm_vector;
    vector<string>  stringlist;
    char fname_vtk[200];

    sprintf(fname_vtk, "%s%d%s", "elmeroutput",0,".vtk");
    writeoutputvtk(nNode, nElem, xcoords, ycoords, elemNodeConn, veloX, veloY, pres, elem_proc_id, fname_vtk);


    std::string fname_field1(argv[2]);
    std::string fname_field;

    for(np=0; np<nproc; ++np)
    {
      sprintf(fname_temp, "%s%s%d", fname_field1.c_str(), ".ep.",np);
      fname_field = fname_temp;
      cout << "Field file name # = " << fname_field << endl;

      ifstream fin(fname_field);

      if(fin.fail())
      {
        cout << " Could not open the Output file" << endl;
        exit(1);
      }

      // read the first two lines of the header
      getline(fin,line); // ASCII
      getline(fin,line); // !File started at:

      // read DOF data
      getline(fin,line); // Degrees of freedom
      getline(fin,line); // flow solution
      getline(fin,line); // velocity 1
      getline(fin,line); // velocity 2
      getline(fin,line); // pressure
      getline(fin,line); // Total DOFs:

      // number of nodes
      getline(fin,line); // Number of Nodes:
      trim(line);
      remove_extra_whitespaces(line, line2);
      split(line2, ' ', stringlist);

      int nNode_local = stoi(stringlist[3]);

      // allocate space for storing the data
      cout << " nNode_local = " << nNode_local << endl;
      perm_vector.resize(nNode_local);

      timesteps_actual=0;
      while(getline(fin,line))  // Time:
      {
        if(timesteps_actual >= timesteps_default)
        {
          cerr << "Number of timesteps exceeds predefined number" << endl;
          cerr << "This program creates the output for 100 timesteps only" << endl;
          break;
        }
        // read X-velocity
        ///////////////////////////////
        getline(fin,line); // velocity 1:
        getline(fin,line); // Perm:
        // read permutation array
        for(ii=0; ii<nNode_local; ++ii)
        {
          getline(fin,line);
          trim(line);
          remove_extra_whitespaces(line, line2);
          split(line2, ' ', stringlist);

          perm_vector[stoi(stringlist[0])-1] = stoi(stringlist[1])-1;
        }

        for(ii=0; ii<nNode_local; ++ii)
        {
          getline(fin,line);
          trim(line);
          split(line, ' ', stringlist);

          solution[timesteps_actual].veloX[nodenums_local[np][ii]] = stof(stringlist[0]);
        }

        // read Y-velocity
        ///////////////////////////////
        // line starting with Perm:
        getline(fin,line); // velocity 2
        getline(fin,line); // Perm:
        for(ii=0; ii<nNode_local; ++ii)
        {
          getline(fin,line);
          trim(line);
          split(line, ' ', stringlist);

          solution[timesteps_actual].veloY[nodenums_local[np][ii]] = stof(stringlist[0]);
        }

        // read pressure
        ///////////////////////////////
        getline(fin,line); // pressure
        getline(fin,line); // Perm:
        for(ii=0; ii<nNode_local; ++ii)
        {
          getline(fin,line);
          trim(line);
          split(line, ' ', stringlist);

          solution[timesteps_actual].pres[nodenums_local[np][ii]] = stof(stringlist[0]);
        }
        timesteps_actual++;
      } // while loop

      fin.close();
    }

    cout << "\n\nTotal times steps = " << timesteps_actual << "\n\n" << endl;

    for(ii=0; ii<timesteps_actual; ++ii)
    {
      sprintf(fname_vtk, "%s%04d%s", "elmeroutput",(ii+1),".vtk");
      writeoutputvtk(nNode, nElem, xcoords, ycoords, elemNodeConn, solution[ii].veloX, solution[ii].veloY, solution[ii].pres, elem_proc_id, fname_vtk);
    }

    cout << "\n\nVTK files generated successfully \n\n\n" << endl;

    return 0;
}











