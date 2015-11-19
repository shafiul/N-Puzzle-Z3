#define LENGTH 4
#define PRIZE 2

void check(int a, int b, int c){
  int position= 0; 
  
  if(a==1){
    position=(position + LENGTH - 2) % LENGTH;
  }else{
    position=(position + 1) % LENGTH;
  }

  if(b==1){
    position=(position + 1) % LENGTH;
  }else{
    position=(position + LENGTH - 2) % LENGTH;
  }

  if(c==1){
    position=(position + LENGTH - 2) % LENGTH;
  }else{
    position=(position + 1) % LENGTH;
  }

  if(position==PRIZE){
    printf("you win :) \n");
    return;
  }
  printf("you loose :( \n");
  return;
}
