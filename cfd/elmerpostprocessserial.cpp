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


void  read_nodes(string& fname, vector<float>& xco, vector<float>& yco)
{
    ifstream fin(fname);

    if(fin.fail())
    {
       cout << " Could not open the Intput file" << '\t' << fname << endl;
       exit(1);
    }

    vector<string>  stringlist;

    // allocate space for storing the data
    xco.clear();
    xco.reserve(10000);
    yco.clear();
    yco.reserve(10000);


    string line;
    int count=0;
    while(getline(fin,line))
    {
      split(line, ' ', stringlist);
      //cout << "stringlist[0]=" << stringlist[0] << endl;

      if(count > xco.capacity())
      {
        cout << "Resizing xco vector " << endl; 
        xco.resize(xco.size()*2, 0.0);
        yco.resize(yco.size()*2, 0.0);
      }

      //xco[count] = stof(stringlist[2]);
      //yco[count] = stof(stringlist[3]);
      //zco[count] = stof(stringlist[4]);

      xco.push_back(stof(stringlist[2]));
      yco.push_back(stof(stringlist[3]));

      //count++;
    }

    xco.shrink_to_fit();
    yco.shrink_to_fit();

    fin.close();

    return;
}



void  read_elements(string& fname, vector<vector<int> >& elemNodeConn)
{
    ifstream fin(fname);

    if(fin.fail())
    {
       cout << " Could not open the Intput file" << '\t' << fname << endl;
       exit(1);
    }

    vector<string>  stringlist;
    vector<int> vecTempInt(3);

    // allocate space for storing the data
    elemNodeConn.clear();
    elemNodeConn.reserve(10000);

    string line;
    int count=0;
    while(getline(fin,line))
    {
      split(line, ' ', stringlist);

      if(count > elemNodeConn.size())
      {
        elemNodeConn.reserve(elemNodeConn.size()*2);
      }

      vecTempInt[0] = stoi(stringlist[3]);
      vecTempInt[1] = stoi(stringlist[4]);
      vecTempInt[2] = stoi(stringlist[5]);

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
      fout << xco[ii] << setw(20) << yco[ii] << setw(20) << 0.0 << endl;
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
      fout << npElem << setw(20) << elemNodeConn[ee][0]-1  << setw(20) << elemNodeConn[ee][1]-1  << setw(20) << elemNodeConn[ee][2]-1 << endl;
    }

    // Cell type, as per VTK
    fout << "CELL_TYPES" << '\t' << nElem << endl;
    for(ee=0; ee<nElem; ++ee)
    {
      fout << n1 << endl;
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
      fout << veloX[ii] << setw(16) << veloY[ii] << setw(16) << 0.0 << endl;
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
      cerr << " You must enter names of 3 files: 1.) nodes, 2.) elements, 3.) field data" << endl;
      return 1;
    }

    vector<float>  xcoords, ycoords;
    vector<vector<int> >  elemNodeConn;

    cout << "Nodal data file   = " << argv[1] << endl;
    cout << "Element data file = " << argv[2] << endl;
    cout << "Field data file   = " << argv[3] << endl;

    ////////////////////////////////////////////
    // read nodal coordinates
    std::string fname_nodes(argv[1]);
    read_nodes(fname_nodes, xcoords, ycoords);
    int nNode = xcoords.size();

    ////////////////////////////////////////////
    // read element-node connectivity
    std::string fname_elems(argv[2]);
    read_elements(fname_elems, elemNodeConn);
    int nElem = elemNodeConn.size();


    ////////////////////////////////////////////
    // read the field data
    string line, line2;

    int ee, ii, jj, kk, n1, n2;

    vector<float>  veloX(nNode, 0.0), veloY(nNode, 0.0), pres(nNode, 0.0);
    vector<float>  vecTempDbl(3);
    vector<int>   perm_vector;
    vector<string>  stringlist;
    char fname_vtk[200];

    std::string fname_field(argv[3]);

    ifstream fin(fname_field);

    if(fin.fail())
    {
       cout << " Could not open the Output file" << endl;
       exit(1);
    }


    // read the first two lines of the header
    getline(fin,line);
    getline(fin,line);

    // read DOF data
    getline(fin,line);
    getline(fin,line);
    getline(fin,line);
    getline(fin,line);
    getline(fin,line);
    getline(fin,line);
    cout << line << endl;

    // number of nodes
    getline(fin,line);
    cout << line << endl;
    trim(line);
    remove_extra_whitespaces(line, line2);
    split(line2, ' ', stringlist);

    cout << stringlist[0] << '\t' << stringlist[1] << '\t' << stringlist[2] << '\t' << stringlist[3] << endl;
    /*
    if( nNode != stoi(stringlist[3]) )
    {
      cerr << "Number of nodes in the mesh and field data does not match" << endl;
      exit(1);
    }
    */

    // allocate space for storing the data
    cout << " nNode = " << nNode << endl;
    perm_vector.resize(nNode);

    cout << " aaaaaaaaaaa " << endl;
    cout << " aaaaaaaaaaa " << endl;

    int  timecount=1;
    // Time instant
    while(getline(fin,line))
    {
      //cout << line << endl;
      //cout << " line " << endl;
      getline(fin,line);

      // read X-velocity
      ///////////////////////////////
      getline(fin,line);
      cout << line << endl;
      // read permutation array
      for(ii=0; ii<nNode; ++ii)
      {
        getline(fin,line);
        trim(line);
        remove_extra_whitespaces(line, line2);
        //cout << line2 << endl;
        split(line2, ' ', stringlist);
        //cout << " bbbbbbbbbb " << endl;
        //cout << stringlist[0] << '\t' << stringlist[1] << endl;
        perm_vector[stoi(stringlist[0])-1] = stoi(stringlist[1])-1;
      }

      for(ii=0; ii<nNode; ++ii)
      {
        getline(fin,line);
        trim(line);
        split(line, ' ', stringlist);
        //cout << stringlist[0] << endl;
        veloX[ii] = stof(stringlist[0]);
        //veloX[perm_vector[ii]] = stof(stringlist[0]);
      }

      // read Y-velocity
      ///////////////////////////////
      // line starting with Perm:
      getline(fin,line);
      getline(fin,line);
      for(ii=0; ii<nNode; ++ii)
      {
        getline(fin,line);
        trim(line);
        split(line, ' ', stringlist);
        //cout << stringlist[0] << endl;
        veloY[ii] = stof(stringlist[0]);
        //veloY[perm_vector[ii]] = stof(stringlist[0]);
      }

      // read pressure
      ///////////////////////////////
      // line with pressure
      getline(fin,line);
      // line starting with Perm:
      getline(fin,line);
      for(ii=0; ii<nNode; ++ii)
      {
        getline(fin,line);
        trim(line);
        split(line, ' ', stringlist);
        //cout << stringlist[0] << endl;
        pres[ii] = stof(stringlist[0]);
        //pres[perm_vector[ii]] = stof(stringlist[0]);
      }

      sprintf(fname_vtk, "%s%04d%s", "elmeroutput",timecount,".vtk");
      writeoutputvtk(nNode, nElem, xcoords, ycoords, elemNodeConn, veloX, veloY, pres, fname_vtk);
      timecount++;
    }
    //


    fin.close();

    return 0;
}











