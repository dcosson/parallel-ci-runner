require 'rspec'

RSpec.describe 'First Spec' do
  it 'should pass' do
    sleep(3)
    expect(1+1).to eq(2)
  end
end
